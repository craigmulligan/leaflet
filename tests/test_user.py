from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from uuid import uuid4

def test_create_user(client: TestClient, db: Session):
    # Test data
    test_email = "test@example.com"

    test_email = f"user-{uuid4()}@x.com"

    # Make a request to create a user
    response = client.post("/user/", files={"email": ("test.txt", test_email)})
    assert response.status_code == 200

    # Check if user was created in the database
    created_user = db.query(User).filter(User.email == test_email).first()
    assert created_user is not None
    assert created_user.email == test_email
