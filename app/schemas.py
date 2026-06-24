from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TitularSchema(BaseModel):
    nome: str
    cpf: str = Field(min_length=11, max_length=11, pattern=r'^\d{11}$')


class TitularPublic(TitularSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TitularList(BaseModel):
    page: int
    per_page: int
    total: int
    items: list[TitularPublic]


class ConcessionariaSchema(BaseModel):
    nome: str
    preco_por_kwh: Decimal = Field(gt=0)


class ConcessionariaPublic(ConcessionariaSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ConcessionariaList(BaseModel):
    page: int
    per_page: int
    total: int
    items: list[ConcessionariaPublic]


class UnidadeConsumidoraSchema(BaseModel):
    codigo: str
    titular_id: int
    concessionaria_id: int


class UnidadeConsumidoraPublic(UnidadeConsumidoraSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UnidadeConsumidoraList(BaseModel):
    page: int
    per_page: int
    total: int
    items: list[UnidadeConsumidoraPublic]


class FaturaSchema(BaseModel):
    unidade_consumidora_id: int
    data_referencia: date
    consumo_total_kwh: Decimal = Field(gt=0)


class FaturaPublic(FaturaSchema):
    id: int
    preco_por_kwh_aplicado: Decimal
    valor_total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FaturaList(BaseModel):
    page: int
    per_page: int
    total: int
    items: list[FaturaPublic]


class Message(BaseModel):
    message: str
