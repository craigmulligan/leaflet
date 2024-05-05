from uuid import uuid4

from sqlalchemy.orm import Session
from app.leaflet import LeafletManager
from app import models 

def test_auth_flow(db: Session):
    test_email = f"user-{uuid4()}@x.com"
    user = models.User(email=test_email)
    db.add(user)
    db.flush()

    manager = LeafletManager(db)

    manager.generate(user)
    
    leaflet = db.query(models.Leaflet).filter_by(user_id=user.id).first()
    assert leaflet
