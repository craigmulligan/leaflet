from freezegun import freeze_time


def test_load_recipes(recipe_loader):
    """
    Given a recipe folder
    1. Check that we return full file name paths
    2. Can randomly select k items
    3. Can load the selected recipes.
    """
    recipe_filenames = recipe_loader.list_recipes()
    assert len(recipe_filenames) == 5
    assert f"{recipe_loader.recipes_path}/BLTA.cook" in recipe_filenames

    assert len(recipe_loader.random_recipes(recipe_filenames, 2)) == 2

    recipes = recipe_loader.load_recipes(recipe_filenames)
    recipe = [recipe for recipe in recipes if recipe.name == "BLTA"][0]

    assert recipe.name == "BLTA"
    assert len(recipe.ingredients) == 9
    assert len(recipe.steps) == 5
    assert len(recipe.cookware) == 1


def test_get_shopping_list(recipe_loader):
    """
    Given a list of recipe filenames we can generate a shopping list.
    """
    recipe_filenames = recipe_loader.list_recipes()
    ingredients = recipe_loader.load_ingredients(recipe_filenames)
    assert len(ingredients) == 40

    ingredients = recipe_loader.load_ingredients(recipe_filenames[0:2])
    assert len(ingredients) == 16


@freeze_time("2013-04-14")
def test_random_recipes(recipe_loader):
    """
    Ensure that given the date + count we return the same recipes.
    """
    recipe_loader
    all_recipes_filesnames = recipe_loader.list_recipes()
    random_recipes_filenames = recipe_loader.random_recipes(all_recipes_filesnames, 3)
    base = recipe_loader.recipes_path

    # assert random_recipes_filenames == [
    #     f"{base}/French Toast.cook",
    #     f"{base}/Ice Cream Cake.cook",
    #     f"{base}/Baked Potato Soup.cook",
    # ]


@freeze_time("2013-04-14")
def test_get_ingredients_and_recipe(user_config_loader, recipe_loader):
    """
    Given a user_config we can load the correct recipes + ingredients.
    """
    user_configs = user_config_loader.load_todays_user_configs()
    # should only be one user on weekday 6
    user_config = user_configs["hey@x.com"]
    ingredients = recipe_loader.ingredients_by_user_config(user_config)
    recipes = recipe_loader.recipes_by_user_config(user_config)

    assert len(recipes) == 2
    assert len(ingredients) == 16
