import glob
from datetime import datetime
import random
import subprocess
from os import path
import tempfile
import shutil
from typing import List, Dict
from dataclasses import dataclass
import json


@dataclass
class Ingredient:
    """Single Ingredient spec"""

    name: str
    amount: str

    def to_html(self):
        return f"<li>{self.name} - {self.amount}</li>"


@dataclass
class Step:
    """Single Recipe Step spec"""

    description: str

    def to_html(self):
        return f"<li>{self.description}</li>"


@dataclass
class Cookware:
    """Single Cookware spec"""

    name: str

    def to_html(self) -> str:
        return f"<li>{self.name}</li>"


class Recipe:
    """Single Ingredient spec"""

    name: str
    ingredients: List[Ingredient]
    steps: List[Step]
    cookware: List[Cookware]

    def __init__(
        self,
        name: str,
        ingredients: List[Dict],
        steps: List[Dict],
        cookware: List[Dict],
    ) -> None:
        self.name = name
        self.ingredients = [Ingredient(**ingredient) for ingredient in ingredients]
        self.steps = [Step(**step) for step in steps]
        self.cookware = [Cookware(**item) for item in cookware]

    def to_html(self) -> str:
        ingredients_list = [ingredient.to_html() for ingredient in self.ingredients]
        steps_list = [step.to_html() for step in self.steps]

        return f"""
            <div>
                <h3>{self.name}</h3>
                <h4>Ingredients</h4>
                <ul>{ingredients_list}</ul>
                <h4>Steps</h4>
                <ul>{steps_list}</ul>
            </div>
        """


def cook_command(*args):
    output = subprocess.check_output(["cook", *args])
    return json.loads(output)


class RecipeLoader:
    def __init__(self, recipes_path: str):
        self.recipes_path = recipes_path

    def list_recipes(self) -> List[str]:
        """
        returns a list of recipes by filename.
        """
        # TODO cache.
        return glob.glob(f"{self.recipes_path}/*.cook")

    def recipes_by_user_config(self, user_config) -> List[Recipe]:
        all_recipes_filesnames = self.list_recipes()
        selected_recipes_filenames = self.random_recipes(
            all_recipes_filesnames, user_config.meal_count
        )
        return self.load_recipes(selected_recipes_filenames)

    def ingredients_by_user_config(self, user_config) -> List[Ingredient]:
        """
        Give a user_config we'll return generate a list of all ingredients
        + recipes.
        """
        all_recipes_filesnames = self.list_recipes()
        selected_recipes_filenames = self.random_recipes(
            all_recipes_filesnames, user_config.meal_count
        )
        return self.load_ingredients(selected_recipes_filenames)

    def load_recipes(self, recipe_filenames: List[str]) -> List[Recipe]:
        """
        Give a list of recipe filenames it'll load them into
        a Recipe object.
        """
        recipes = []
        for filename in recipe_filenames:
            recipe_data = cook_command(
                "recipe", "read", filename, "--output-format", "json"
            )
            _, filename = path.split(filename)
            name = path.splitext(filename)[0]
            recipe = Recipe(name, **recipe_data)
            recipes.append(recipe)

        return recipes

    def random_recipes(self, recipe_filenames: List[str], k: int) -> List[str]:
        """
        Randomly selects k recipes.
        Seeded by datetime.
        """
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        random.seed(date)
        return random.sample(recipe_filenames, k)

    def load_ingredients(self, recipe_filenames: List[str]) -> List[Ingredient]:
        """
        Gets cumulative shopping list for selected recipes.
        """
        ingredients = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for filename in recipe_filenames:
                shutil.copy2(filename, temp_dir)

            shopping_list_data = cook_command(
                "shopping-list", temp_dir, "--output-format", "json"
            )
            for ingredient in shopping_list_data["INGREDIENTS"]:
                ingredients.append(Ingredient(**ingredient))

        return ingredients
