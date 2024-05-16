from app.db import SessionLocal
from app import models
from app.llm import LLM
from app.leaflet import LeafletManager
from app.mailer import MailManager

if __name__ == "__main__":
    db = SessionLocal()
    email = "x@x.com"
    try:
        llm = LLM()
        mailer = MailManager()
        manager = LeafletManager(db, llm, mailer)
        user = db.query(models.User).filter_by(email=email).first()

        if user is None:
            user = models.User(email=email)
            db.add(user)
            db.commit()
            db.refresh(user)

        manager.generate(user)
    finally:
        db.close()
