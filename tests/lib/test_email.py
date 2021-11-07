from freezegun import freeze_time
from unittest.mock import patch


@freeze_time("2013-04-08")
def test_email_format(email, dummy_user_config, recipe_loader):
    ingredients, recipes = recipe_loader.ingredients_and_recipes_by_user_config(
        dummy_user_config
    )

    html = email._format(recipes, ingredients)

    recipe = recipes[0]
    ingredient = ingredients[0]

    # do some adhoc format checking.
    assert f"<h3>{recipe.name}</h3>" in html
    assert ingredient.to_html() in html


@freeze_time("2013-04-08")
def test_email_format_and_send(email, dummy_user_config, recipe_loader, email_client):
    ingredients, recipes = recipe_loader.ingredients_and_recipes_by_user_config(
        dummy_user_config
    )
    html = email._format(recipes, ingredients)

    email.format_and_send(dummy_user_config, recipes, ingredients)
    assert email_client.send.called_with(
        From=email.sender,
        to=dummy_user_config.email,
        Subject="Your weekly meals & ingredients",
        HtmlBody=html,
    )
