from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Concessionaria, UnidadeConsumidora
from app.schemas import (
    ConcessionariaList,
    ConcessionariaPublic,
    ConcessionariaSchema,
)

router = APIRouter(prefix='/concessionarias', tags=['concessionarias'])


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=ConcessionariaPublic,
)
def create_concessionaria(
    concessionaria: ConcessionariaSchema,
    session: Session = Depends(get_session),
):
    db_concessionaria = Concessionaria(
        nome=concessionaria.nome,
        preco_por_kwh=concessionaria.preco_por_kwh,
    )

    try:
        session.add(db_concessionaria)
        session.commit()
        session.refresh(db_concessionaria)

        return db_concessionaria
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Concessionária já cadastrada',
        )


@router.get('/', response_model=ConcessionariaList)
def read_concessionarias(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    total = session.scalar(select(func.count(Concessionaria.id)))

    concessionarias = session.scalars(
        select(Concessionaria).offset((page - 1) * per_page).limit(per_page)
    ).all()

    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': concessionarias,
    }


@router.get(
    '/{concessionaria_id}',
    response_model=ConcessionariaPublic,
)
def read_concessionaria(
    concessionaria_id: int,
    session: Session = Depends(get_session),
):
    concessionaria = session.get(Concessionaria, concessionaria_id)

    if not concessionaria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concessionária não encontrada',
        )

    return concessionaria


@router.put(
    '/{concessionaria_id}',
    response_model=ConcessionariaPublic,
)
def update_concessionaria(
    concessionaria_id: int,
    concessionaria: ConcessionariaSchema,
    session: Session = Depends(get_session),
):
    db_concessionaria = session.get(Concessionaria, concessionaria_id)

    if not db_concessionaria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concessionária não encontrada',
        )

    db_concessionaria.nome = concessionaria.nome
    db_concessionaria.preco_por_kwh = concessionaria.preco_por_kwh

    try:
        session.commit()
        session.refresh(db_concessionaria)

        return db_concessionaria
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Concessionária já cadastrada',
        )


@router.delete(
    '/{concessionaria_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_concessionaria(
    concessionaria_id: int,
    session: Session = Depends(get_session),
):
    db_concessionaria = session.get(Concessionaria, concessionaria_id)

    if not db_concessionaria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Concessionária não encontrada',
        )

    unidade_vinculada = session.scalar(
        select(UnidadeConsumidora).where(
            UnidadeConsumidora.concessionaria_id == concessionaria_id
        )
    )

    if unidade_vinculada:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=(
                'Não é possível deletar a concessionária, pois existem '
                'unidades consumidoras associadas a ela'
            ),
        )

    session.delete(db_concessionaria)
    session.commit()
