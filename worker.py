from app.db import SessionLocal
from app.llm import LLM
from app.leaflet import LeafletManager
from app.mailer import mail_manager
from app.main import app

if __name__ == "__main__":
    db = SessionLocal()
    try:
        llm = LLM()
        manager = LeafletManager(app, db, llm, mail_manager)
        manager.generate_all()
    finally:
        db.close()
