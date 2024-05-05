from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from typing import List

from app.leaflet import LeafletManager
from app import models 

def test_generate(db: Session, create_user):
    user = create_user() 

    manager = LeafletManager(db)

    manager.generate(user)
    
    leaflet = db.query(models.Leaflet).filter_by(user_id=user.id).first()
    assert leaflet

def test_get_candidates(db: Session, create_user):
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
                leaflet.created_at = datetime.now() - timedelta(days=random.randint(8*i, 14*i))

    assert len(expected_candidates) == 10
    manager = LeafletManager(db)

    candidates = []
    for c in manager.get_user_candidates(chunk_size=2):
        candidates.extend(c)

    assert len(candidates) == len(expected_candidates)
    assert candidates == expected_candidates
