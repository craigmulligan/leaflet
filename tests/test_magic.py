from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from uuid import uuid4

def test_auth_flow(client: TestClient, db: Session):
    # It should generate a magic link.
    # In test or dev mode it should return the magic link
    # then "requesting that magic link"
    # should log the user in + confirm their email.
    test_email = "test@example.com"

    test_email = f"user-{uuid4()}@x.com"

    # Make a request to create a user
    response = client.post("/magic/", files={"email": ("test.txt", test_email)})
    assert response.status_code == 200

    # Check if user was created in the database
    created_user = db.query(User).filter(User.email == test_email).first()
    assert created_user is not None
    assert created_user.email == test_email
