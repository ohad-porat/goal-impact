"""Database setup and initialization for FBRef API."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Event

# Database configuration
DATABASE_URL = 'sqlite:///db/fbref_database.db'

# Create an engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a sessionmaker
Session = sessionmaker(bind=engine)

def get_db():
    """Get database session."""
    db = Session()
    try:
        yield db
    finally:
        db.close()
