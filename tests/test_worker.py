from sqlalchemy.orm import Session
from app.leaflet import LeafletManager
from app import models 

def test_auth_flow(db: Session, create_user):
    user = create_user() 

    manager = LeafletManager(db)

    manager.generate(user)
    
    leaflet = db.query(models.Leaflet).filter_by(user_id=user.id).first()
    assert leaflet
