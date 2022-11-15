import logging
from typing import List
from flask import g
from app.models import User, Recipe
from app import database
from dataclasses import dataclass
from datetime import datetime

from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

pint = UnitRegistry()


@dataclass
class Digest:
    created_at: datetime
    recipes: List[Recipe]
    user: User

    def shopping_list(self) -> List[str]:
        """
        For each recipe we and the similar recipes.
        """
        ingredients = {}

        for recipe in self.recipes:
            for ingredient in recipe.ingredients:
                if ingredients.get(ingredient.name):
                    ingredients[ingredient.name].append(ingredient)
                else:
                    ingredients[ingredient.name] = [ingredient]

        failures = []
        shopping_list = {}

        for key, value in ingredients.items():
            total = 0

            for v in value:
                try:
                    total += pint.Quantity(v.quantity, v.unit)
                except UndefinedUnitError:
                    logging.warning(f"couldn't get normalize unit:{v.unit}")
                    failures.append(v)
                except ValueError:
                    logging.warning(f"couldn't get normalize quantity:{v.quantity}")
                    failures.append(v)
                except DimensionalityError:
                    breakpoint()

            if total > 0:
                shopping_list[key] = total

        output = []
        for key, value in shopping_list.items():
            magnitude = round(value.magnitude * self.user.serving, 2)
            units = "" if value.dimensionless else pint.get_symbol(str(value.units))
            output.append(f"{key}: {magnitude} {units}".strip())

        for f in failures:
            output.append(
                f"{f.name}: {f.quantity * self.user.serving} {f.unit}".strip()
            )

        output.sort()
        return output

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
        return Digest(now, recipes, user)

    def save_digest(self, digest):
        for recipe in digest.recipes:
            self.db.digest_insert(digest.created_at, recipe.id, digest.user.id)


def get() -> RecipeManager:
    manager = getattr(g, RecipeManager.context_key, None)
    if manager is None:
        manager = RecipeManager()
        setattr(g, RecipeManager.context_key, manager)

    return manager
