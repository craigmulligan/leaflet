from typing import List
from flask import g
from app.models import User, Recipe
from app import database
from dataclasses import dataclass
from datetime import datetime

from pint import DimensionalityError
from app.collector.ingredient import pint, unit_to_str


@dataclass
class Leaflet:
    created_at: datetime
    recipes: List[Recipe]
    user: User

    def shopping_list(self) -> List[str]:
        """
        For each recipe we add all ingredients
        and calculate totals.
        """
        totals = {}

        for recipe in self.recipes:
            for ingredient in recipe.ingredients:
                totals.setdefault(ingredient.name, [{"total": 0, "unit": None}])
                q = pint.Quantity(ingredient.quantity, ingredient.unit)

                attempts = 0

                while True:
                    try:
                        quantity_type = totals[ingredient.name][attempts]
                    except:
                        break

                    try:
                        quantity_type["total"] += q
                        quantity_type["unit"] = q.units
                        break
                    except DimensionalityError:
                        attempts += 1

        output = []
        for ingredient_name, quantities in totals.items():
            for data in quantities:
                unit = unit_to_str(data["unit"])
                quantity = (
                    data["total"].magnitude
                    if isinstance(data["total"], pint.Quantity)
                    else data["total"]
                ) * self.user.serving

                output.append(f"{ingredient_name}: {round(quantity, 2)} {unit}".strip())

        output.sort()
        return output


class LeafletManager:
    context_key = "_leaflet_manager"

    def __init__(self) -> None:
        self.db = database.get()

    def generate(self, user: User) -> Leaflet:

        """
        This is where the magic happens, but rn
        it's pretty simple.

        1. First pick a random recipe.
        2. Find another <user.recipe_per_leaflet:int> recipes with similar ingredients.
        """

        db = database.get()
        random_recipe_id = db.recipe_random(user.id)
        similar_recipe_ids = db.recipe_similar(random_recipe_id, user.recipes_per_week)

        recipes = []
        for recipe_id in [random_recipe_id, *similar_recipe_ids]:
            recipes.append(db.recipe_get(recipe_id))

        now = datetime.utcnow()
        return Leaflet(now, recipes, user)

    def save(self, leaflet):
        for recipe in leaflet.recipes:
            self.db.leaflet_insert(leaflet.created_at, recipe.id, leaflet.user.id)


def get() -> LeafletManager:
    manager = getattr(g, LeafletManager.context_key, None)
    if manager is None:
        manager = LeafletManager()
        setattr(g, LeafletManager.context_key, manager)

    return manager