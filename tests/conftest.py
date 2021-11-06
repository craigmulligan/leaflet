import pytest
from lib.user_config import UserConfigLoader
from lib.recipe import RecipeLoader


@pytest.fixture()
def user_config_loader():
    return UserConfigLoader("tests/data/db/users")


@pytest.fixture()
def recipe_loader():
    return RecipeLoader("tests/data/recipe")
