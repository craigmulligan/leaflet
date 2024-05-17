from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum number of connections to overflow beyond pool_size
    pool_timeout=30,  # Time in seconds to wait before giving up on getting a connection from the pool
    pool_recycle=1800,  # Time in seconds after which connections are recycled
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
