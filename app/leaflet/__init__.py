import logging
from sqlalchemy.orm import Session
from app import models
from app.llm import LLM


class LeafletManager():
    def __init__(self, db: Session) -> None:
        self.db = db
        pass
        
    def generate(self, user: models.User):
        """
        Given a users settings

        Generate 3 recipes + a shopping list
        and return to caller.
        """
        llm = LLM()
        try:
            content = llm.generate()

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

                # TODO add a real placeholder.
                recipe.image = "https://placeholder"

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

                for generated_shopping_list_item in recipe_generated.ingredients:
                    shopping_list_item = models.ShoppingListItem()
                    self.db.add(shopping_list_item)
                    shopping_list_item.recipe = recipe
                    shopping_list_item.description = generated_shopping_list_item.description
                    shopping_list_item.amount = generated_shopping_list_item.amount
                    shopping_list_item.unit = generated_shopping_list_item.unit

            # save to db.
            self.db.commit()
            logging.info(f"successfull saved {leaflet}")
        except Exception as e:
            raise e
        return