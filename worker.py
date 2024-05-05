from app.db import SessionLocal
from app.leaflet import LeafletManager 

if __name__ == "__main__":
    db = SessionLocal()
    try:
        manager = LeafletManager(db)
        manager.generate()
    finally:
        db.close()
