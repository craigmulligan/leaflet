import uuid


def test_recipe_random(db, seeded_recipe_ids, dummy_user, dummy_recipe_id):
    user = dummy_user()
    leaflet_id = str(uuid.uuid4())

    for recipe_id in seeded_recipe_ids:
        if recipe_id != dummy_recipe_id:
            db.leaflet_entry_insert(leaflet_id, recipe_id, user.id)

    recipe_id = db.recipe_random(user.id)
    assert recipe_id == dummy_recipe_id
