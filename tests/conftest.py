import pytest
from unittest.mock import Mock
import uuid

from app import create_app
from app.models import User
from app.mail import MailManager
from app.leaflet_manager import LeafletManager, get as get_leaflet_manager
from app.session import session
from app import database
from flask import g
from celery import Task


@pytest.fixture(scope="function", autouse=True)
def app():
    """Session-wide test `Flask` application."""
    # Establish an application context before running the tests.
    app = create_app({"DB_URL": ":memory:", "TESTING": True})
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture()
def leaflet_manager_mock():
    mock = Mock()

    setattr(g, LeafletManager.context_key, mock)
    return mock


@pytest.fixture()
def leaflet_manager():
    return get_leaflet_manager()


@pytest.fixture(autouse=True)
def mail_manager_mock():
    mock = Mock()

    setattr(g, MailManager.context_key, mock)
    return mock


@pytest.fixture(scope="function", autouse=True)
def db():
    _db = database.get()
    _db.setup()
    return _db


@pytest.fixture(scope="function")
def seeded_recipe_ids(db):
    return [
        "6b67ac5e278df57361d232baeea4fcd93a7050ec",
        "56cd7fb0e5bd654e4eaa0955042163f7ca55f085",
        "72335e9f76c017f81c0c8c36c4ec1e0aad6be6fb",
        "f83a1421367928da867fbe449d5110aa0621ded5",
        "0607603cf8f1702cee1dbad2ff91e08ffdebae9c",
        "92994cd172837bbbaf5eac5bae5d4107eefecd86",
        "2639b056b11beac1f8293127540f5a2d85578331",
    ]


@pytest.fixture(scope="function", autouse=True)
def seed(db, seeded_recipe_ids):
    return db.recipe_load(
        "data/recipe",
        recipe_ids=seeded_recipe_ids,
    )


@pytest.fixture(scope="function")
def dummy_user(db):
    """
    util function to create a test case user.
    """

    def create_dummy_user(email=None, recipes_per_week=1, serving=1) -> User:
        if email is None:
            email = str(uuid.uuid4()) + "@x.com"
        user = db.user_create(email=email)
        user = db.user_update(user.id, recipes_per_week, serving)
        return user

    return create_dummy_user


@pytest.fixture(scope="function")
def signin(client):
    """
    util function to create a test case user.
    """

    def inner(user: User) -> None:
        with client.session_transaction() as sesh:
            session.flask_session = sesh
            session.signin(user)
            session.flask_session = None

    return inner


@pytest.fixture(scope="function", autouse=True)
def monkey_patch_celery_async(monkeypatch):
    """
    This ensures that celery tasks are called locally
    so you can assert their results within the test
    without running the worker.
    """
    monkeypatch.setattr("celery.Task.apply_async", Task.apply)


@pytest.fixture(scope="function")
def dummy_recipe_id():
    return "56cd7fb0e5bd654e4eaa0955042163f7ca55f085"


@pytest.fixture(scope="function")
def mock_recipe_random(monkeypatch, dummy_recipe_id):
    """
    This ensures that celery tasks are called locally
    so you can assert their results within the test
    without running the worker.
    """
    mock = Mock(return_value=dummy_recipe_id)
    monkeypatch.setattr("app.database.Db.recipe_random", mock)
