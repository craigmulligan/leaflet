from app.db import SessionLocal
from app import models
from app.llm import LLM
from app.leaflet import LeafletManager

if __name__ == "__main__":
    db = SessionLocal()
    try:
        llm = LLM()
        manager = LeafletManager(db, llm)
        user = db.query(models.User).filter_by(email="x@x.com").one()

        manager.generate(user)
    finally:
        db.close()
