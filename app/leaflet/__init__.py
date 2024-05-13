import time
from datetime import datetime, timedelta
import logging
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from app import models
from app.llm import LLM


class LeafletManager:
    def __init__(self, db: Session, llm: LLM) -> None:
        self.db = db
        self.llm = llm
        self.default_user_prompt = (
            "I usually cook for 2 people, I'd like my recipes in the metric system."
        )

    def get_user_candidates(self, chunk_size=20):
        """
        returns an iter() that returns a chunk of List<User>
        who have got NO Leaflet where created_at is >
        1 week old.
        """
        one_week_ago = datetime.now() - timedelta(days=7)
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

        try:
            content = self.llm.generate(
                prompt, [recipe.title for recipe in previous_recipes]
            )

            print("previous_recipes", previous_recipes)
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
                recipe.image = self.llm.generate_image(recipe_generated)

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
                    recipe_ingredient.description = (
                        generated_recipe_ingredient.description
                    )
                    recipe_ingredient.amount = generated_recipe_ingredient.amount
                    recipe_ingredient.unit = generated_recipe_ingredient.unit

                for generated_shopping_list_item in recipe_generated.ingredients:
                    shopping_list_item = models.ShoppingListItem()
                    self.db.add(shopping_list_item)
                    shopping_list_item.recipe = recipe
                    shopping_list_item.description = (
                        generated_shopping_list_item.description
                    )
                    shopping_list_item.amount = generated_shopping_list_item.amount
                    shopping_list_item.unit = generated_shopping_list_item.unit

                embeddings = self.llm.generate_embeddings(str(recipe))
                recipe_embedding = models.RecipeEmbedding()
                self.db.add(recipe_embedding)
                recipe_embedding.recipe = recipe
                recipe_embedding.embedding = embeddings

            # save to db.
            self.db.commit()
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Execution time: {elapsed_time} seconds")
            logging.info(f"successfull saved {leaflet}")
        except Exception as e:
            raise e
        return
