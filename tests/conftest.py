import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal

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
