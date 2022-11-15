from flask import render_template
from app.models import User


def test_user_get_authenticated(client, dummy_user, signin):
    """
    Asserts user page is correctly rendered.
    """
    user = dummy_user()
    signin(user)

    response = client.get(f"/user/{user.id}")
    assert response.status_code == 200
    assert render_template("user.html", user=user) == response.data.decode("utf-8")


def test_user_update_user_authenticated_no_data(client, dummy_user, signin):
    """
    Asserts you can't update user info without all data.
    """
    user = dummy_user()
    signin(user)

    response = client.post(f"/user/{user.id}")
    assert response.status_code == 422


def test_user_update_user_authenticated(client, dummy_user, signin, db):
    """
    Asserts you can't update user info without all data.
    """
    user = dummy_user()
    signin(user)
    recipes_per_week = 2
    serving = 3

    assert user.recipes_per_week != recipes_per_week
    assert user.serving != serving

    response = client.post(
        f"/user/{user.id}",
        data={"serving": serving, "recipes_per_week": recipes_per_week},
        follow_redirects=True,
    )
    assert response.status_code == 200

    updated_user = db.user_get_by_id(user.id)

    assert updated_user.serving == serving
    assert updated_user.recipes_per_week == recipes_per_week
    assert render_template("user.html", user=updated_user) == response.data.decode(
        "utf-8"
    )


def test_user_get_forbidden(client, dummy_user, signin):
    """
    Asserts a user can not view another user page.
    """
    john = dummy_user(email="john@x.com")
    jane = dummy_user(email="jane@x.com")
    signin(john)

    response = client.get(f"/user/{jane.id}")
    assert response.status_code == 403


def test_user_get_does_not_exist(client, dummy_user, signin):
    """
    Asserts a 404 is returned for a non-existent user.
    """
    user = dummy_user()
    signin(user)

    response = client.get(f"/user/104")
    assert response.status_code == 404


def test_user_get_unauthenticated(client, dummy_user):
    """
    Asserts if the requestor is not logged in
    they are redirected to the signin page.
    """
    user = dummy_user()
    response = client.get(f"/user/{user.id}")
    assert response.status_code == 302
