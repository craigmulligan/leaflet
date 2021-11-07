import logging
import os
from datetime import datetime
from random import Random

from lib.runner import Runner
from lib.email import Email
from lib.user_config import UserConfigLoader
from lib.recipe import RecipeLoader
from sendgrid import SendGridAPIClient

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    sendgrid_api_key = os.environ["SENDGRID_API_KEY"]
    sender_email = os.environ["SENDER_EMAIL"]

    seed = int(
        datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    )
    # This should ensure if we re-run the job
    # on the same date user should get the same email.
    random = Random(seed)

    logging.info("Running digest")
    user_config_loader = UserConfigLoader("data/db/users")
    recipe_loader = RecipeLoader("data/recipe", random.sample)

    email_client = SendGridAPIClient(sendgrid_api_key)
    email = Email(sender_email, email_client)

    oks, noks = Runner(user_config_loader, recipe_loader, email).run()

    for ok in oks:
        logging.info(f"Successfully sent {ok.email} digest")

    for nok in noks:
        logging.error(f"Failed to send {nok.email} - {nok.message}")
