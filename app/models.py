from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Titular(Base):
    __tablename__ = 'titulares'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(11), nullable=False, unique=True)

    unidades_consumidoras = relationship(
        'UnidadeConsumidora',
        back_populates='titular',
    )


class Concessionaria(Base):
    __tablename__ = 'concessionarias'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    preco_por_kwh = Column(Numeric(14, 5), nullable=False)

    unidades_consumidoras = relationship(
        'UnidadeConsumidora',
        back_populates='concessionaria',
    )


class UnidadeConsumidora(Base):
    __tablename__ = 'unidades_consumidoras'

    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), nullable=False, unique=True)

    titular_id = Column(
        Integer,
        ForeignKey('titulares.id'),
        nullable=False,
    )

    concessionaria_id = Column(
        Integer,
        ForeignKey('concessionarias.id'),
        nullable=False,
    )

    titular = relationship(
        'Titular',
        back_populates='unidades_consumidoras',
    )

    concessionaria = relationship(
        'Concessionaria',
        back_populates='unidades_consumidoras',
    )

    faturas = relationship(
        'Fatura',
        back_populates='unidade_consumidora',
    )


class Fatura(Base):
    __tablename__ = 'faturas'

    id = Column(Integer, primary_key=True)

    unidade_consumidora_id = Column(
        Integer,
        ForeignKey('unidades_consumidoras.id'),
        nullable=False,
    )

    data_referencia = Column(Date, nullable=False)
    consumo_total_kwh = Column(Numeric(14, 2), nullable=False)
    preco_por_kwh_aplicado = Column(Numeric(14, 5), nullable=False)
    valor_total = Column(Numeric(14, 2), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    unidade_consumidora = relationship(
        'UnidadeConsumidora',
        back_populates='faturas',
    )
