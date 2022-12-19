from flask import render_template
from html import escape
from tests.conftest import Contains


def test_user_get_authenticated(client, dummy_user, signin, seeded_recipe_ids, app):
    """
    Asserts user page is correctly rendered.
    """
    user = dummy_user()
    signin(user)

    response = client.get(f"/user/{user.id}")
    assert response.status_code == 200
    data = response.data.decode("utf-8")
    recipe_count = len(seeded_recipe_ids)
    assert render_template("user.html", user=user, recipe_count=recipe_count) == data 
    assert str(f"Total recipes in {app.config['APP_NAME']}: {recipe_count}" ) in data 


def test_user_update_user_authenticated_no_data(client, dummy_user, signin):
    """
    Asserts you can't update user info without all data.
    """
    user = dummy_user()
    signin(user)

    response = client.post(f"/user/{user.id}")
    assert response.status_code == 200
    assert "Error updating settings" in response.text


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

    # Check that we set the value to the current setting.
    assert f'value={updated_user.serving}' in response.text  
    assert f'value={updated_user.recipes_per_week}' in response.text  


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


def test_user_leaflet_post(client, dummy_user, signin, db, leaflet_manager, mail_manager_mock):
    """
    Asserts user can request a new leaflet
    """
    user = dummy_user()
    signin(user)

    assert len(db.leaflet_get_all_by_user(user.id)) == 0

    response = client.post(f"/user/{user.id}/leaflet", follow_redirects=True)

    assert len(db.leaflet_get_all_by_user(user.id)) == 1

    leaflet_ids = db.leaflet_get_all_by_user(user.id)
    leaflet = leaflet_manager.get(user, leaflet_ids[0])

    assert response.status_code == 200

    mail_manager_mock.send.assert_called_once_with(
        user.email,
        f"Leaflet #1",
        Contains("Shopping List"),
    )

    for recipe in leaflet.recipes:
        assert escape(recipe.title) in response.text


def test_user_leaflet_get(client, dummy_user, signin, leaflet_manager):
    """
    Asserts user can get an existing leaflet
    """
    user = dummy_user()
    signin(user)
    leaflet = leaflet_manager.generate(user)
    leaflet_id = leaflet_manager.save(leaflet)

    response = client.get(f"/user/{user.id}/leaflet/{leaflet_id}")

    assert response.status_code == 200

    for recipe in leaflet.recipes:
        assert escape(recipe.title) in response.text
