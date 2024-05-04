from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from uuid import uuid4

def test_auth_flow(client: TestClient, db: Session):
    # It should generate a magic link.
    # In test or dev mode it should return the magic link
    # then "requesting that magic link"
    # should log the user in + confirm their email.


    # assert we are redirected to /signin
    response = client.get("/signin")
    assert "Signin" in response.text

    test_email = "test@example.com"
    test_email = f"user-{uuid4()}@x.com"

    # Make a request to create a user
    response = client.post("/auth/magic/", data={"email": test_email})
    assert response.status_code == 200

    # Check if user was created in the database
    created_user = db.query(User).filter(User.email == test_email).first()
    assert created_user is not None
    assert created_user.email == test_email

    # Now follow the magic link
    magic_url = response.context["magic_url"]
    assert magic_url

    response = client.get(magic_url)

    # Check we are on the dashboard
    assert response.url.path == "/dashboard/"
    assert test_email in response.text


    response = client.get("/dashboard/logout")
    assert response.url.path == "/signin"
