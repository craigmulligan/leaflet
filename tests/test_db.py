import uuid


def test_recipe_random(db, seeded_recipe_ids, dummy_user, dummy_recipe_id, mock_recipe_random):
    user = dummy_user()
    leaflet_id = str(uuid.uuid4())

    for recipe_id in seeded_recipe_ids:
        if recipe_id != dummy_recipe_id:
            db.leaflet_entry_insert(leaflet_id, recipe_id, user.id)

    recipe_id = db.recipe_random(user.id)
    assert recipe_id == dummy_recipe_id


def test_leaflet_get_all_by_user(db, seeded_recipe_ids, dummy_user, mock_recipe_random, leaflet_manager):
    user = dummy_user(recipes_per_week=4)
    leaflet = leaflet_manager.generate(user)
    leaflet_manager.save(leaflet)

    leaflets = db.leaflet_get_all_by_user(user.id)    
    assert len(leaflets) == 1

    leaflet = leaflet_manager.generate(user)
    leaflet_manager.save(leaflet)

    leaflets = db.leaflet_get_all_by_user(user.id)    
    assert len(leaflets) == 2
