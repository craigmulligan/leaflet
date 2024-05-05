from .db import SessionLocal
import os

def is_dev():
    return os.environ.get("ENV") != "production"


def send_email(email: str):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
