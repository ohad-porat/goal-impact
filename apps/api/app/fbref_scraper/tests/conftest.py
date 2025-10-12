"""Shared pytest configuration and fixtures."""

import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base


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
    """Create a database session for testing."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
    
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


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    from core.config import ScraperConfig
    
    return ScraperConfig(
        SELECTED_NATIONS=['England', 'Italy'],
        YEAR_RANGE=(2020, 2024),
        DEBUG=True,
        DATABASE_URL='sqlite:///:memory:',
        REQUEST_TIMEOUT=30,
        FBREF_BASE_URL='https://fbref.com',
        LOG_LEVEL='DEBUG'
    )
