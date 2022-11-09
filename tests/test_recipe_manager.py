def test_get_digest(
    dummy_user,
    recipe_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    digest = recipe_manager.get_digest(user)
    assert len(digest.recipes) == 3
    ids = [recipe.id for recipe in digest.recipes]

    # Ids should be static because mock the randomizer and
    # only load a subset of recipes for tests.
    assert ids == [
        "56cd7fb0e5bd654e4eaa0955042163f7ca55f085",
        "6b67ac5e278df57361d232baeea4fcd93a7050ec",
        "72335e9f76c017f81c0c8c36c4ec1e0aad6be6fb",
    ]


def test_save_digest(
    dummy_user,
    recipe_manager,
    db,
    mock_recipe_random,
    dummy_recipe_id,
):
    user = dummy_user()
    digest = recipe_manager.get_digest(user)

    assert len(db.digest_get_all_by_user(user.id)) == 0

    recipe_manager.save_digest(digest)

    assert len(db.digest_get_all_by_user(user.id)) == 1
