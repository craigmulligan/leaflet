import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from tests.llm_mock import LLMMock

@pytest.fixture()
def client():
    client = TestClient(app)
    return client

@pytest.fixture()
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def monkeypatch_llm(monkeypatch):
    monkeypatch.setattr("app.llm.LLM", LLMMock)
