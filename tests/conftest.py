from datetime import datetime
import pytest
from lib.user_config import UserConfigLoader, UserConfig
from lib.recipe import RecipeLoader
from lib.email import Email
from lib.runner import Runner


def mock_sampler(items, n):
    return items[0:n]


@pytest.fixture()
def user_config_loader():
    return UserConfigLoader("tests/data/db/users")


@pytest.fixture()
def recipe_loader():
    return RecipeLoader("tests/data/recipe", mock_sampler)


@pytest.fixture()
def email(postmark_client):
    return Email("sender@x.com", postmark_client)


@pytest.fixture()
def dummy_user_config():
    return UserConfig("dummy@x.com", datetime.now(), 2, 1, 0)


@pytest.fixture()
def runner(user_config_loader, recipe_loader, email):
    return Runner(user_config_loader, recipe_loader, email)
