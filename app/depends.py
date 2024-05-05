from .db import SessionLocal

# Dependency
# TODO move to utils
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

