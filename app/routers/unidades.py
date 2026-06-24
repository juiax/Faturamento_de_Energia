from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Concessionaria, Fatura, Titular, UnidadeConsumidora
from app.schemas import (
    FaturaList,
    UnidadeConsumidoraList,
    UnidadeConsumidoraPublic,
    UnidadeConsumidoraSchema,
)

router = APIRouter(prefix='/unidades', tags=['unidades'])


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UnidadeConsumidoraPublic,
)
def create_unidade(
    unidade: UnidadeConsumidoraSchema,
    session: Session = Depends(get_session),
):
    titular = session.get(Titular, unidade.titular_id)

    if not titular:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Titular não encontrado',
        )

    concessionaria = session.get(Concessionaria, unidade.concessionaria_id)

    if not concessionaria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concessionária não encontrada',
        )

    db_unidade = UnidadeConsumidora(
        codigo=unidade.codigo,
        titular_id=unidade.titular_id,
        concessionaria_id=unidade.concessionaria_id,
    )

    try:
        session.add(db_unidade)
        session.commit()
        session.refresh(db_unidade)

        return db_unidade
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Unidade já cadastrada',
        )


@router.get(
    '/',
    response_model=UnidadeConsumidoraList,
)
def read_unidades(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    total = session.scalar(select(func.count(UnidadeConsumidora.id)))
    unidades = session.scalars(
        select(UnidadeConsumidora)
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()

    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': unidades,
    }


@router.get(
    '/{unidade_id}',
    response_model=UnidadeConsumidoraPublic,
)
def read_unidade(
    unidade_id: int,
    session: Session = Depends(get_session),
):
    unidade = session.get(UnidadeConsumidora, unidade_id)

    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não encontrada',
        )

    return unidade


@router.put(
    '/{unidade_id}',
    response_model=UnidadeConsumidoraPublic,
)
def update_unidade(
    unidade_id: int,
    unidade: UnidadeConsumidoraSchema,
    session: Session = Depends(get_session),
):
    db_unidade = session.get(UnidadeConsumidora, unidade_id)

    if not db_unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não encontrada',
        )

    titular = session.get(Titular, unidade.titular_id)

    if not titular:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Titular não encontrado',
        )

    concessionaria = session.get(Concessionaria, unidade.concessionaria_id)

    if not concessionaria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concessionária não encontrada',
        )

    db_unidade.codigo = unidade.codigo
    db_unidade.titular_id = unidade.titular_id
    db_unidade.concessionaria_id = unidade.concessionaria_id

    try:
        session.commit()
        session.refresh(db_unidade)

        return db_unidade
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Unidade já cadastrada',
        )


@router.delete(
    '/{unidade_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_unidade(
    unidade_id: int,
    session: Session = Depends(get_session),
):
    db_unidade = session.get(UnidadeConsumidora, unidade_id)

    if not db_unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não encontrada',
        )

    if db_unidade.faturas:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Não é possível deletar a unidade,'
            'pois existem faturas associadas a ela',
        )

    session.delete(db_unidade)
    session.commit()


@router.get(
    '/{unidade_id}/faturas',
    response_model=FaturaList,
)
def read_historico_faturas(
    unidade_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    unidade = session.get(UnidadeConsumidora, unidade_id)

    if not unidade:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Unidade não encontrada',
        )

    total = session.scalar(
        select(func.count(Fatura.id)).where(
            Fatura.unidade_consumidora_id == unidade_id
        )
    )

    faturas = session.scalars(
        select(Fatura)
        .where(Fatura.unidade_consumidora_id == unidade_id)
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
