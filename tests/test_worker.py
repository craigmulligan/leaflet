import pytest
from datetime import datetime, timedelta
import random
from unittest.mock import MagicMock, call
from sqlalchemy.orm import Session
from typing import List

from app.leaflet import LeafletManager
from app import models
from app import config
from tests.conftest import CreateUser


@pytest.mark.vcr
def test_user_prompt_is_used(
    db: Session,
    leaflet_manager: LeafletManager,
    llm: MagicMock,
    create_user: CreateUser,
):
    user = create_user()
    leaflet_manager.generate(user)
    leaflet = db.query(models.Leaflet).filter_by(user_id=user.id).one()
    llm.generate.assert_called_with(leaflet_manager.default_user_prompt, [])

    llm.generate_embeddings.assert_has_calls(
        [call(str(recipe)) for recipe in leaflet.recipes]
    )

    user.prompt = "I like tomato"
    db.commit()

    leaflet_manager.generate(user)

    llm.generate.assert_called_with(
        user.prompt, [recipe.title for recipe in leaflet.recipes]
    )


@pytest.mark.vcr
def test_worker_generate_all(
    db: Session,
    leaflet_manager: LeafletManager,
    llm: MagicMock,
    create_user: CreateUser,
    mailer: MagicMock,
):
    user = create_user()
    leaflet_manager.generate_all()
    leaflet = db.query(models.Leaflet).filter_by(user_id=user.id).one()
    llm.generate.assert_called_with(leaflet_manager.default_user_prompt, [])

    llm.generate_embeddings.assert_has_calls(
        [call(str(recipe)) for recipe in leaflet.recipes]
    )

    args, _ = mailer.send.call_args
    assert args[0] == user.email
    assert args[1] == "Leaflet #1"
    assert f"{config.HOST_URL}/dashboard/leaflet/{leaflet.id}" in args[2]

    for recipe in leaflet.recipes:
        assert f"{config.HOST_URL}/dashboard/recipe/{recipe.id}" in args[2]


def test_get_candidates(
    db: Session, leaflet_manager: LeafletManager, create_user: CreateUser
):
    """
    Create 15 users
    users 1-5: have never received a leaflet.

    users 5-10: have a leaflet within a week old.

    users 10-15 have no leaflets within a week old.
    """

    expected_candidates: List[models.User] = []

    for n in range(1, 16):
        user = create_user()

        if n <= 5:
            expected_candidates.append(user)

        if 5 < n <= 10:
            leaflet = models.Leaflet()
            db.add(leaflet)
            leaflet.user = user
            leaflet.created_at = datetime.now() - timedelta(days=random.randint(0, 6))

        if 10 < n <= 15:
            expected_candidates.append(user)

            for i in range(1, 5):
                # lets create a bunch of old leaflets for these users.
                leaflet = models.Leaflet()
                db.add(leaflet)
                leaflet.user = user
                leaflet.created_at = datetime.now() - timedelta(
                    days=random.randint(8 * i, 14 * i)
                )

    assert len(expected_candidates) == 10

    candidates = []
    for c in leaflet_manager.get_user_candidates(chunk_size=2):
        candidates.extend(c)

    assert len(candidates) == len(expected_candidates)
    assert candidates == expected_candidates
