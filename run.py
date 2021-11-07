import logging
from lib import run
from lib.email import Email
from lib.user_config import UserConfigLoader
from lib.recipe import RecipeLoader
from random import sample
from unittest.mock import Mock

if __name__ == "__main__":
    user_config_loader = UserConfigLoader("data/db/users")
    recipe_loader = RecipeLoader("data/recipe", sample)
    email = Mock()
    oks, noks = run(user_config_loader, recipe_loader, email)

    for ok in oks:
        logging.info("Successfully sent {ok.email} digest")

    for nok in noks:
        logging.exception("Failed to send {nok.email} - {nok.message}")
