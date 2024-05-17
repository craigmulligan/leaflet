from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User


def test_authenticated_user_can_view(client: TestClient, create_user, signin):
    user = create_user()
    response = client.get("/dashboard")
    ## check we redirect
    assert response.url.path == "/signin"
    signin(user)
    response = client.get("/dashboard")
    assert response.url.path == "/dashboard/"
