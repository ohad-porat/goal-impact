"""Database setup and initialization for FBRef API."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv('.env.local')

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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
