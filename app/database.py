from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base

DATABASE_URL = 'sqlite:///./database.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session
