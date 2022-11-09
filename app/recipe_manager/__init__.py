from typing import List
from flask import g
from app.models import User, Recipe
from app import database
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Digest:
    created_at: datetime
    recipes: List[Recipe]
    user_id: int

    def shopping_list(self):
        """
        For each recipe we and the similar recipes.
        """

    def to_html(self):
        pass

    def to_plain_text(self):
        pass


class RecipeManager:
    context_key = "_recipe_manager"

    def __init__(self) -> None:
        self.db = database.get()

    def get_digest(self, user: User) -> Digest:

        """
        This is where the magic happens, but rn
        it's pretty simple.

        1. First pick a random recipe.
        2. Find another <user.recipe_per_digest:int> recipes with similar ingredients.
        """

        db = database.get()
        random_recipe_id = db.recipe_random(user.id)
        similar_recipe_ids = db.recipe_similar(random_recipe_id, user.recipes_per_week)
        # TODO:
        # Convert recipe to user.serving size.

        recipes = []
        for recipe_id in [random_recipe_id, *similar_recipe_ids]:
            recipes.append(db.recipe_get(recipe_id))

        now = datetime.utcnow()
        return Digest(now, recipes, user.id)

    def save_digest(self, digest):
        for recipe in digest.recipes:
            self.db.digest_insert(digest.created_at, recipe.id, digest.user_id)


def get() -> RecipeManager:
    manager = getattr(g, RecipeManager.context_key, None)
    if manager is None:
        manager = RecipeManager()
        setattr(g, RecipeManager.context_key, manager)

    return manager
