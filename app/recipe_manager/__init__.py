import logging
from typing import List
from flask import g
from app.models import User, Recipe
from app import database
from dataclasses import dataclass
from datetime import datetime

from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

pint = UnitRegistry()
pint.define("cloves = 1")
pint.define("bunches = 1")


@dataclass
class Digest:
    created_at: datetime
    recipes: List[Recipe]
    user: User

    def shopping_list(self) -> List[str]:
        """
        For each recipe we add all ingredients
        and calculate totals.
        """
        ingredients = {}

        for recipe in self.recipes:
            factor = self.user.serving / recipe.yields

            for ingredient in recipe.ingredients:
                ingredient.quantity = ingredient.quantity * factor
                ingredients.setdefault(ingredient.name, []).append(ingredient)

        failures = []
        quantities = {}

        for key, value in ingredients.items():
            for v in value:
                try:
                    quantities.setdefault(key, []).append(
                        pint.Quantity(v.quantity, v.unit)
                    )
                except UndefinedUnitError as e:
                    logging.warning(
                        f"couldn't get normalize unit:{v.unit} - adding without unit."
                    )
                    quantities.setdefault(key, []).append(pint.Quantity(v.quantity))
                except ValueError as e:
                    logging.warning(f"couldn't get normalize quantity:{v.quantity}")
                    failures.append([e, v])
                except DimensionalityError as e:
                    failures.append([e, v])

        output = []

        for ingredient_name, values in quantities.items():
            total = 0
            units = ""

            for value in values:
                total += round(value.magnitude, 2)
                units = (
                    ""
                    if str(value.units) == "dimensionless"
                    else pint.get_symbol(str(value.units))
                )

            output.append(f"{ingredient_name}: {total} {units}".strip())

        output.sort()
        return output


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
