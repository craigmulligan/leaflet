from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app import config


# Note pgbouncer will handle connection pooling
# so it's not necesscary here.
engine = create_engine(
    config.SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
