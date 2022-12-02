from datetime import datetime


def test_recipe_random(db, seeded_recipe_ids, dummy_user, dummy_recipe_id):
    user = dummy_user()

    for recipe_id in seeded_recipe_ids:
        if recipe_id != dummy_recipe_id:
            db.leaflet_insert(recipe_id, user.id)

    recipe_id = db.recipe_random(user.id)
    assert recipe_id == dummy_recipe_id
