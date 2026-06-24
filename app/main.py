from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database import create_db_and_tables, engine
from app.routers import concessionarias, faturas, titulares, unidades
from app.seed import seed_concessionarias

app = FastAPI(title='API de Faturamento de Energia')


@app.on_event('startup')
def on_startup():
    create_db_and_tables()

    with Session(engine) as session:
        seed_concessionarias(session)


@app.get('/')
def read_root():
    return {'message': 'API de Faturamento de Energia'}


app.include_router(titulares.router)
app.include_router(unidades.router)
app.include_router(concessionarias.router)
app.include_router(faturas.router)
