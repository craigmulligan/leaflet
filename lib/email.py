from typing import List
from lib.recipe import Recipe, Ingredient
from lib.user_config import UserConfig
from postmarker.core import PostmarkClient


class Email:
    def __init__(self, sender: str, client: PostmarkClient) -> None:
        self.client = client
        self.sender = sender

    def _format(self, recipes: List[Recipe], ingredients: List[Ingredient]):
        """
        Given recipes and ingredeients it will return formatted html.
        """
        ingredients_list = [ingredient.to_html() for ingredient in ingredients]
        recipes_list = [recipe.to_html() for recipe in recipes]

        return f"""<html>
          <head></head>
          <body>
            <h1>Your weekly vegetarian shopping list & recipes.<h1>
            <h2>
                Ingredients
            </h2>
            <ul>
            {ingredients_list} 
            </ul>
            <h2>
                Recipes 
            </h2>
            {recipes_list} 
          </body>
        </html>
      """

    def _send(self, to, html):
        self.client.emails.send(
            From=self.sender,
            To=to,
            Subject="Your weekly meals & ingredients",
            HtmlBody=html,
        )

    def format_and_send(
        self,
        user_config: UserConfig,
        recipes: List[Recipe],
        ingredients: List[Ingredient],
    ):
        """
        Given recipes and ingredeients it will construct & send an email.
        """
        html = self._format(recipes, ingredients)
        return self._send(user_config.email, html)
