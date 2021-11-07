import logging
import os

from lib.runner import Runner
from lib.email import Email
from lib.user_config import UserConfigLoader
from lib.recipe import RecipeLoader
from postmarker.core import PostmarkClient
from random import sample

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    postmark_server_token = os.environ["POSTMARK_SERVER_TOKEN"]

    logging.info("Running digest")
    user_config_loader = UserConfigLoader("data/db/users")
    recipe_loader = RecipeLoader("data/recipe", sample)
    email_client = PostmarkClient(postmark_server_token)
    email = Email("hey@craigmulligan.com", email_client)
    oks, noks = Runner(user_config_loader, recipe_loader, email).run()

    for ok in oks:
        logging.info(f"Successfully sent {ok.email} digest")

    for nok in noks:
        logging.exception(f"Failed to send {nok.email} - {nok.message}")
