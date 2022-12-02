def test_generate(
    dummy_user,
    leaflet_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    leaflet = leaflet_manager.generate(user)
    assert len(leaflet.recipes) == 1
    ids = [recipe.id for recipe in leaflet.recipes]

    # Ids should be static because mock the randomizer and
    # only load a subset of recipes for tests.
    assert ids == [
        "56cd7fb0e5bd654e4eaa0955042163f7ca55f085",
    ]


def test_save_leaflet(
    dummy_user,
    leaflet_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    leaflet = leaflet_manager.generate(user)

    assert len(db.leaflet_get_all_by_user(user.id)) == 0

    leaflet_manager.save(leaflet)

    assert len(db.leaflet_get_all_by_user(user.id)) == 1


def test_get_shopping_list(
    dummy_user,
    leaflet_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user(serving=1)
    leaflet = leaflet_manager.generate(user)
    shopping_list = leaflet.shopping_list()

    assert len(shopping_list) == 12
    last_item = shopping_list[-1]
    assert last_item == "yellow pepper: 0.5"
    assert "garlic: 1 cloves" in shopping_list

    # now lets scale the servings and check the shopping_list adjusts accordingly.
    serving_size = 2
    user = dummy_user(serving=serving_size)
    leaflet = leaflet_manager.generate(user)
    shopping_list = leaflet.shopping_list()

    assert len(shopping_list) == 12
    last_item = shopping_list[-1]

    assert last_item == "yellow pepper: 1.0"

    user = dummy_user(recipes_per_week=2)
    leaflet = leaflet_manager.generate(user)
    shopping_list = leaflet.shopping_list()
    assert len(shopping_list) == 24