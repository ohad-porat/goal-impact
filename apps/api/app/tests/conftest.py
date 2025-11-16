"""Shared pytest configuration and fixtures for all tests."""

import os
import sys
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add app directory to path for imports
api_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app_dir = os.path.join(api_dir, 'app')
sys.path.insert(0, api_dir)
sys.path.insert(0, app_dir)

from app.models import Base


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Create a database session for testing.
    
    This fixture provides a clean database session for each test.
    After the test, it rolls back any changes and cleans up the database.
    """
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
    
    # Clean up all tables after test
    cleanup_session = Session()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            cleanup_session.execute(table.delete())
        cleanup_session.commit()
    finally:
        cleanup_session.close()


@pytest.fixture
def temp_db_file():
    """Create a temporary database file for file-based tests."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    if os.path.exists(db_path):
        os.unlink(db_path)
