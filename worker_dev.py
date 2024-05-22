from app.db import SessionLocal
from app import models
from app.llm import LLM
from app.leaflet import LeafletManager
from app.mailer import mail_manager
from app.main import app

if __name__ == "__main__":
    # Utility to generate a leaflet for a single user
    db = SessionLocal()
    email = "x@x.com"
    try:
        llm = LLM()
        manager = LeafletManager(app, db, llm, mail_manager)
        user = db.query(models.User).filter_by(email="x@x.com").one()

        if user is None:
            user = models.User(email=email)
            db.add(user)
            db.commit()
            db.refresh(user)

        manager.generate(user)
    finally:
        db.close()
