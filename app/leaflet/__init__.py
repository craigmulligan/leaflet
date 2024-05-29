import time
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from app import models
from app.llm import LLM
from app.mailer import MailManager
from app import config
from app.storage import upload_image

templates = Jinja2Templates(directory="app/templates")


class LeafletManager:
    def __init__(
        self, app: FastAPI, db: Session, llm: LLM, mailer: MailManager
    ) -> None:
        self.app = app
        self.db = db
        self.llm = llm
        self.mailer = mailer
        self.default_user_prompt = (
            "I usually cook for 2 people, I'd like my recipes in the metric system."
        )

    def get_user_candidates(self, chunk_size=20, **kwargs):
        """
        returns an iter() that returns a chunk of List<User>
        who have got NO Leaflet where created_at is >
        1 week old.
        """
        one_week_ago = datetime.now() - timedelta(**kwargs)
        last_id = None

        while True:
            # Query for users who have no leaflets created within the last week
            query = (
                self.db.query(models.User)
                .outerjoin(models.Leaflet)
                .filter(
                    or_(
                        models.Leaflet.id == None,  # noqa
                        models.Leaflet.created_at < one_week_ago,
                    )
                )
            )

            # If last_id is not None, filter users with id greater than last_id
            if last_id is not None:
                query = query.filter(models.User.id > last_id)

            # Fetch the next chunk of users
            users_chunk = query.order_by(models.User.id).limit(chunk_size).all()

            # If no more users, break the loop
            if not users_chunk:
                break

            # Yield the chunk of users
            yield users_chunk

            # Update last_id to the id of the last user in the chunk
            last_id = users_chunk[-1].id

    def generate(self, user: models.User):
        """
        Given a users settings

        Generate 3 recipes + a shopping list
        and return to caller.
        """

        start_time = time.time()
        prompt = user.prompt or self.default_user_prompt
        previous_recipes = (
            self.db.query(models.Recipe)
            .join(models.Leaflet)
            .filter(models.Leaflet.user_id == user.id)
            .order_by(desc(models.Recipe.created_at))
            .limit(10)
            .all()
        )

        content = self.llm.generate(
            prompt, [recipe.title for recipe in previous_recipes]
        )

        # create a leaflet
        leaflet = models.Leaflet()
        leaflet.user = user
        self.db.add(leaflet)

        for recipe_generated in content.recipes:
            recipe = models.Recipe()
            recipe.leaflet = leaflet
            recipe.title = recipe_generated.title
            recipe.description = recipe_generated.description
            recipe.estimated_time = recipe_generated.estimated_time
            recipe.servings = recipe_generated.servings

            image_url = self.llm.generate_image(recipe_generated)

            if image_url:
                recipe.image = upload_image(image_url)

            self.db.add(recipe)

            for i, generated_recipe_step in enumerate(recipe_generated.steps):
                recipe_step = models.RecipeStep()
                self.db.add(recipe_step)
                recipe_step.recipe = recipe
                recipe_step.index = i
                recipe_step.description = generated_recipe_step.description

            for generated_recipe_ingredient in recipe_generated.ingredients:
                recipe_ingredient = models.RecipeIngredient()
                self.db.add(recipe_ingredient)
                recipe_ingredient.recipe = recipe
                recipe_ingredient.description = generated_recipe_ingredient.description
                recipe_ingredient.amount = generated_recipe_ingredient.amount
                recipe_ingredient.unit = generated_recipe_ingredient.unit

            embeddings = self.llm.generate_embeddings(str(recipe))
            recipe_embedding = models.RecipeEmbedding()
            self.db.add(recipe_embedding)
            recipe_embedding.recipe = recipe
            recipe_embedding.embedding = embeddings

        # save to db.
        self.db.commit()
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(
            f"Leaflet generation time for user: {user.id} time: {elapsed_time} seconds"
        )
        logging.info(f"successfull saved {leaflet.id}")
        return leaflet

    def absolute_url_for(self, name: str, **params) -> str:
        # Create a dummy request object with the base URL to generate absolute URLs
        url = config.HOST_URL

        return urljoin(url, self.app.url_path_for(name, **params))

    def generate_all(self):
        start_time = time.time()
        logging.info("Generating leaflets")
        for users in self.get_user_candidates(hours=1):
            for user in users:
                try:
                    logging.info(f"generating leaflet for {user.id}")
                    leaflet = self.generate(user)
                    leaflet_count = (
                        self.db.query(models.Leaflet).filter_by(user_id=user.id).count()
                    )
                    body = templates.get_template("email.html").render(
                        {"url_for": self.absolute_url_for, "leaflet": leaflet}
                    )
                    self.mailer.send(user.email, f"Leaflet #{leaflet_count}", body)
                except Exception:
                    logging.exception(f"Failed to generate leafet for user {user.id}")
        elapsed_time = time.time() - start_time
        logging.info(f"Generating leaflets execution time: {elapsed_time} seconds")
