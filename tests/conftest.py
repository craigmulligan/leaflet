from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db import SessionLocal, engine
from app import models
from app.leaflet import LeafletManager
from tests.llm_mock import LLMMock


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def create_user(db: Session):
    def inner(email=None):
        if email is None:
            email = f"user-{uuid4()}@x.com"

        user = models.User(email=email)
        db.add(user)
        db.flush()
        return user

    return inner


@pytest.fixture()
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clear_db():
    """
    Clear the db between tests
    """
    models.BaseModel.metadata.drop_all(engine)
    models.BaseModel.metadata.create_all(engine)
    yield
    models.BaseModel.metadata.drop_all(engine)


@pytest.fixture()
def leaflet_manager(db: Session):
    llm = LLMMock()
    return LeafletManager(db, llm)
