import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from abastecepyme.infrastructure.database.models.base import Base
from abastecepyme.infrastructure.database.models.element_model import ElementModel
from abastecepyme.infrastructure.database.models.dependency_model import DependencyModel
from abastecepyme.infrastructure.database.session import get_db
from abastecepyme.presentation.main import app

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTest = sessionmaker(bind=engine_test, autoflush=False, autocommit=False)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine_test)