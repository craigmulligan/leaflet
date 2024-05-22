from time import sleep
from app.db import SessionLocal
from app.llm import LLM
from app.leaflet import LeafletManager
from app.mailer import mail_manager
from app.main import app

if __name__ == "__main__":
    # TODO we should switch to using
    # fly.ios scheduler instead of a always running
    # worker.
    while True:
        db = SessionLocal()
        try:
            llm = LLM()
            manager = LeafletManager(app, db, llm, mail_manager)
            manager.generate_all()
        finally:
            db.close()
        # sleep for an hour
        sleep(60 * 60)
