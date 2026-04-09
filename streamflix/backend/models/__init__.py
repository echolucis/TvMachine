from .database import Base, engine, SessionLocal

# Import all models to ensure they are registered with Base
from . import database


def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session (dependency for FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
