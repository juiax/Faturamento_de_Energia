from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, Concessionaria

DATABASE_URL = 'sqlite:///./database.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session


def seed_concessionarias(session: Session):
    copel = session.scalar(
        select(Concessionaria).where(Concessionaria.nome == 'copel')
    )

    if not copel:
        session.add(
            Concessionaria(
                nome='copel',
                preco_por_kwh=Decimal('0.64242'),
            )
        )

    celesc = session.scalar(
        select(Concessionaria).where(Concessionaria.nome == 'celesc')
    )

    if not celesc:
        session.add(
            Concessionaria(nome='celesc', preco_por_kwh=Decimal('0.69568'))
        )

    session.commit()
