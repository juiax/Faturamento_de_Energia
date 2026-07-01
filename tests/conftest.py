import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import Base
from app.seed import seed_concessionarias


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_concessionarias(session)
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
