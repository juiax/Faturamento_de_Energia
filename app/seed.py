from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Concessionaria


def seed_concessionarias(session: Session):
    concessionarias_padrao = [
        {
            'nome': 'copel',
            'preco_por_kwh': Decimal('0.64242'),
        },
        {
            'nome': 'celesc',
            'preco_por_kwh': Decimal('0.69568'),
        },
    ]

    for concessionaria in concessionarias_padrao:
        existe = session.scalar(
            select(Concessionaria).where(
                Concessionaria.nome == concessionaria['nome']
            )
        )

        if not existe:
            session.add(Concessionaria(**concessionaria))

    session.commit()
