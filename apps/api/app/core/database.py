"""Database setup and initialization for FBRef API."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

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
