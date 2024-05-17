import pytest
from fastapi.testclient import TestClient
from app.leaflet import LeafletManager
from tests.conftest import CreateUser, Signin


def test_authenticated_user_can_view(
    client: TestClient, create_user: CreateUser, signin: Signin
):
    user = create_user()
    response = client.get("/dashboard")
    ## check we redirect
    assert response.url.path == "/signin"
    signin(user)
    response = client.get("/dashboard")
    assert response.url.path == "/dashboard/"


@pytest.mark.vcr
def test_views(
    leaflet_manager: LeafletManager,
    create_user: CreateUser,
    client: TestClient,
    signin: Signin,
):
    user = create_user()
    leaflet = leaflet_manager.generate(user)
    signin(user)

    response = client.get("/dashboard")

    assert f"/leaflet/{leaflet.id}" in response.text
