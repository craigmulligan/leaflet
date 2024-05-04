import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app.db import SessionLocal

# Define SQLAlchemy model
Base = declarative_base()

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
