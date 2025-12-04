"""Shared pytest configuration and fixtures."""

import os
import sys
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

api_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
app_dir = os.path.join(api_dir, "app")
sys.path.insert(0, api_dir)
sys.path.insert(0, app_dir)

from app.models import Base
from app.tests.utils.factories import (
    CompetitionFactory,
    EventFactory,
    GoalValueLookupFactory,
    MatchFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    StatsCalculationMetadataFactory,
    TeamFactory,
    TeamStatsFactory,
)


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=test_engine)
    session = Session()

    for factory_class in [
        NationFactory,
        CompetitionFactory,
        SeasonFactory,
        TeamFactory,
        PlayerFactory,
        MatchFactory,
        EventFactory,
        PlayerStatsFactory,
        TeamStatsFactory,
        GoalValueLookupFactory,
        StatsCalculationMetadataFactory,
    ]:
        factory_class._meta.sqlalchemy_session = session

    yield session

    for factory_class in [
        NationFactory,
        CompetitionFactory,
        SeasonFactory,
        TeamFactory,
        PlayerFactory,
        MatchFactory,
        EventFactory,
        PlayerStatsFactory,
        TeamStatsFactory,
        GoalValueLookupFactory,
        StatsCalculationMetadataFactory,
    ]:
        factory_class._meta.sqlalchemy_session = None

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
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    yield db_path

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    from app.fbref_scraper.core import ScraperConfig

    return ScraperConfig(
        SELECTED_NATIONS=["England", "Italy"],
        YEAR_RANGE=(2020, 2024),
        DEBUG=True,
        REQUEST_TIMEOUT=30,
        FBREF_BASE_URL="https://fbref.com",
        LOG_LEVEL="DEBUG",
    )
