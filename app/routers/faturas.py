from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Concessionaria, Fatura, UnidadeConsumidora
from app.schemas import FaturaList, FaturaPublic, FaturaSchema

router = APIRouter(prefix='/faturas', tags=['faturas'])


def calcular_valor_total(consumo: Decimal, preco: Decimal) -> Decimal:
    return (consumo * preco).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )


def inicio_e_fim_do_mes(data: date):
    inicio = data.replace(day=1)

    if data.month == 12:
        fim = data.replace(year=data.year + 1, month=1, day=1)
    else:
        fim = data.replace(month=data.month + 1, day=1)

    return inicio, fim


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=FaturaPublic,
)
def create_fatura(
    fatura: FaturaSchema,
    session: Session = Depends(get_session),
):
    unidade = session.get(UnidadeConsumidora, fatura.unidade_consumidora_id)

    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade consumidora não encontrada',
        )

    inicio_mes, fim_mes = inicio_e_fim_do_mes(fatura.data_referencia)

    fatura_existente = session.scalar(
        select(Fatura).where(
            Fatura.unidade_consumidora_id == fatura.unidade_consumidora_id,
            Fatura.data_referencia >= inicio_mes,
            Fatura.data_referencia < fim_mes,
        )
    )

    if fatura_existente:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Já existe fatura para esta unidade neste mês',
        )

    concessionaria = session.get(Concessionaria, unidade.concessionaria_id)

    if not concessionaria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concessionária não encontrada',
        )

    preco = concessionaria.preco_por_kwh
    valor_total = calcular_valor_total(fatura.consumo_total_kwh, preco)

    db_fatura = Fatura(
        unidade_consumidora_id=fatura.unidade_consumidora_id,
        data_referencia=fatura.data_referencia,
        consumo_total_kwh=fatura.consumo_total_kwh,
        preco_por_kwh_aplicado=preco,
        valor_total=valor_total,
    )

    session.add(db_fatura)
    session.commit()
    session.refresh(db_fatura)

    return db_fatura


@router.get('/', response_model=FaturaList)
def read_faturas(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    total = session.scalar(select(func.count(Fatura.id)))

    faturas = session.scalars(
        select(Fatura)
        .order_by(Fatura.data_referencia.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()

    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': faturas,
    }


@router.get('/{fatura_id}', response_model=FaturaPublic)
def read_fatura(
    fatura_id: int,
    session: Session = Depends(get_session),
):
    fatura = session.get(Fatura, fatura_id)

    if not fatura:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Fatura não encontrada',
        )

    return fatura


@router.put('/{fatura_id}', response_model=FaturaPublic)
def update_fatura(
    fatura_id: int,
    fatura: FaturaSchema,
    session: Session = Depends(get_session),
):
    db_fatura = session.get(Fatura, fatura_id)

    if not db_fatura:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Fatura não encontrada',
        )

    unidade = session.get(UnidadeConsumidora, fatura.unidade_consumidora_id)

    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade consumidora não encontrada',
        )

    inicio_mes, fim_mes = inicio_e_fim_do_mes(fatura.data_referencia)

    fatura_existente = session.scalar(
        select(Fatura).where(
            Fatura.unidade_consumidora_id == fatura.unidade_consumidora_id,
            Fatura.data_referencia >= inicio_mes,
            Fatura.data_referencia < fim_mes,
            Fatura.id != fatura_id,
        )
    )

    if fatura_existente:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Já existe fatura para esta unidade neste mês',
        )

    preco = unidade.concessionaria.preco_por_kwh
    valor_total = calcular_valor_total(fatura.consumo_total_kwh, preco)

    db_fatura.unidade_consumidora_id = fatura.unidade_consumidora_id
    db_fatura.data_referencia = fatura.data_referencia
    db_fatura.consumo_total_kwh = fatura.consumo_total_kwh
    db_fatura.preco_por_kwh_aplicado = preco
    db_fatura.valor_total = valor_total

    session.commit()
    session.refresh(db_fatura)

    return db_fatura


@router.delete(
    '/{fatura_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_fatura(
    fatura_id: int,
    session: Session = Depends(get_session),
):
    fatura = session.get(Fatura, fatura_id)

    if not fatura:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Fatura não encontrada',
        )

    session.delete(fatura)
    session.commit()
