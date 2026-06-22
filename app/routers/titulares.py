from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Query, Session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import Titular
from app.schemas import Message, TitularList, TitularPublic, TitularSchema

router = APIRouter(prefix='/titulares', tags=['titulares'])


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=TitularPublic,
)
def create_titular(
    titular: TitularSchema,
    session: Session = Depends(get_session),
):
    db_titular = Titular(nome=titular.nome, cpf=titular.cpf)

    try:
        session.add(db_titular)
        session.commit()
        session.refresh(db_titular)

        return db_titular
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='CPF já cadastrado',
        )
    

@router.get(
    '/',
    response_model=TitularList,
)
def read_titulares(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    total = session.scalar(select(func.count(Titular.id)))
    titulares = session.scalars(
        select(Titular)
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()

    return{
        'page': page,
        'per_page': per_page,
        'total': total,
        'items': titulares,
    }


@router.get(
        '/{titular_id}',
        response_model=TitularPublic,
    )
def read_titular(
    titular_id: int,
    session: Session = Depends(get_session),
):
    titular = session.get(Titular, titular_id)

    if not titular:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Titular não encontrado',
        )

    return titular


@router.put(
    '/{titular_id}',
    response_model=TitularPublic,
)
def update_titular(
    titular_id: int,
    titular: TitularSchema,
    session: Session = Depends(get_session),
):
    db_titular = session.get(Titular, titular_id)

    if not db_titular:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Titular não encontrado',
        )
    
    try:
        db_titular.nome = titular.nome
        db_titular.cpf = titular.cpf

        session.commit()
        session.refresh(db_titular)

        return db_titular
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='CPF já cadastrado',
        )
    

@router.delete(
    '/{titular_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_titular(
    titular_id: int,
    session: Session = Depends(get_session),
):
    titular = session.get(Titular, titular_id)

    if not titular:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Titular não encontrado',
        )

    session.delete(titular)
    session.commit()

    return None