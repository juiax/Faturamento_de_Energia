from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import titulares

app = FastAPI(title='API de Faturamento de Energia')


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.get('/')
def read_root():
    return {'message': 'API de Faturamento de Energia'}


app.include_router(titulares.router)
