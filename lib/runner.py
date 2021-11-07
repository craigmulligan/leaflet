from typing import Tuple, List
from lib.user_config import UserConfigLoader
from lib.recipe import RecipeLoader
from lib.email import Email
from lib.result import Result


class Runner:
    def __init__(
        self,
        user_config_loader: UserConfigLoader,
        recipe_loader: RecipeLoader,
        email: Email,
    ):
        self.user_config_loader = user_config_loader
        self.recipe_loader = recipe_loader
        self.email = email

    def run(self) -> Tuple[List[Result], List[Result]]:
        """
        1. Load userconfigs
        2. Check if today is the day they'd like their shopping list.
        3. Pick User[recipe no] number of random recipes.
        4. Compile shopping list from recipes.
        5. Email Shopping list + recipes to user.
        """
        oks = []
        noks = []
        user_configs = self.user_config_loader.load_todays_user_configs()

        for user_email, user_config in user_configs.items():
            try:
                recipes = self.recipe_loader.recipes_by_user_config(user_config)
                ingredients = self.recipe_loader.ingredients_by_user_config(user_config)
                self.email.format_and_send(user_config, recipes, ingredients)
                oks.append(Result(user_email, 0))
            except Exception as e:
                noks.append(Result(user_email, 1, str(e)))

        return oks, noks
