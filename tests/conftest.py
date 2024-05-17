from uuid import uuid4
from typing import Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from unittest.mock import MagicMock
from app.db import SessionLocal, engine
from app import models
from app.leaflet import LeafletManager
from app.llm import LLM


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
        db.commit()
        db.refresh(user)
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
    Clear the db between + after tests
    """
    models.BaseModel.metadata.drop_all(engine)
    models.BaseModel.metadata.create_all(engine)
    yield
    models.BaseModel.metadata.drop_all(engine)


@pytest.fixture()
def llm():
    llm = LLM()
    return MagicMock(wraps=llm)


@pytest.fixture()
def leaflet_manager(db: Session, llm: LLM):
    return LeafletManager(db, llm, MagicMock())


@pytest.fixture(scope="module")
def vcr_config() -> Dict[str, Any]:
    return {
        "filter_headers": ["authorization", "host"],
        "ignore_localhost": True,
        "record_mode": "once",
    }


@pytest.fixture
def signin(client):
    def sign_user_in(user: models.User):
        client.cookies.set("user_id", str(user.id))

    return sign_user_in
