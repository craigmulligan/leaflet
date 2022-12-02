def test_generate(
    dummy_user,
    recipe_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    leaflet = recipe_manager.generate(user)
    assert len(leaflet.recipes) == 2
    ids = [recipe.id for recipe in leaflet.recipes]

    # Ids should be static because mock the randomizer and
    # only load a subset of recipes for tests.
    assert ids == [
        "56cd7fb0e5bd654e4eaa0955042163f7ca55f085",
        "72335e9f76c017f81c0c8c36c4ec1e0aad6be6fb",
    ]


def test_save_leaflet(
    dummy_user,
    recipe_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    leaflet = recipe_manager.generate(user)

    assert len(db.leaflet_get_all_by_user(user.id)) == 0

    recipe_manager.save(leaflet)

    assert len(db.leaflet_get_all_by_user(user.id)) == 1


def test_get_shopping_list(
    dummy_user,
    recipe_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    leaflet = recipe_manager.generate(user)
    shopping_list = leaflet.shopping_list()

    assert len(shopping_list) == 25
    last_item = shopping_list[-1]
    assert last_item == "yellow pepper: 0.5"
    assert "garlic: 2 cloves" in shopping_list

    # now lets scale the servings and check the shopping_list adjusts accordingly.
    serving_size = 2
    db.user_update(user.id, user.recipes_per_week, serving_size)
    user = db.user_get_by_id(user.id)
    leaflet = recipe_manager.generate(user)
    shopping_list = leaflet.shopping_list()

    assert len(shopping_list) == 25
    last_item = shopping_list[-1]

    assert last_item == "yellow pepper: 1.0"
