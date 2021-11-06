# def run(user_configs_path: str, recipes_path: str) -> bool:
#     """
#     1. Load userconfigs
#     2. Check if today is the day they'd like their shopping list.
#     3. Pick User[recipe no] number of random recipes.
#     4. Compile shopping list from recipes.
#     5. Email Shopping list + recipes to user.
#     """
#     user_configs = load_user_configs(user_configs_path)
#     all_recipes = list_recipes(recipes_path)
#     results = []

#     for user_config in user_configs:
#         recipes = random_recipes(all_recipes, user_config.meal_count)
#         ingredients = get_shopping_list(recipes)
#         load_recipes = load_recipes(recipes)
#         result = send_email(user_config, recipes, ingredients)
#         results.append(result)

#     print(results)
