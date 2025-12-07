"""Shared pytest configuration and fixtures for all tests."""

import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.functions import Function

# Add app directory to path for imports
api_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app_dir = os.path.join(api_dir, "app")
sys.path.insert(0, api_dir)
sys.path.insert(0, app_dir)

from app.core.database import get_db
from app.main import app
from app.models import Base
from app.schemas.clubs import (
    ClubInfo,
    CompetitionInfo as ClubCompetitionInfo,
    NationBasic,
    NationDetailed,
    PlayerBasic,
    TeamStatsInfo,
)
from app.schemas.common import NationInfo
from app.schemas.players import (
    CompetitionInfo,
    PlayerInfo,
    PlayerStats,
    SeasonDisplay,
    TeamInfo,
)
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


@compiles(Function, "sqlite")
def compile_function_sqlite(element, compiler, **kw):
    """Override function compilation for SQLite, specifically string_agg."""
    if hasattr(element, "name") and element.name == "string_agg":
        clauses = list(element.clauses)
        if len(clauses) >= 2:
            column = clauses[0]
            delimiter = clauses[1]
            return f"group_concat({compiler.process(column, **kw)}, {compiler.process(delimiter, **kw)})"
        else:
            column = clauses[0]
            return f"group_concat({compiler.process(column, **kw)})"

    return compiler.visit_function(element, **kw)


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
    """Create a database session for testing.

    This fixture provides a clean database session for each test.
    After the test, it rolls back any changes and cleans up the database.
    """
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
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    yield db_path

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client(db_session):
    """Create a FastAPI TestClient using the test database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """Set up factory-boy to use the test database session."""
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
        factory_class._meta.sqlalchemy_session = db_session

    yield

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


# Schema test fixtures
@pytest.fixture
def empty_player_stats() -> PlayerStats:
    """Create PlayerStats with all None values."""
    return PlayerStats(
        matches_played=None,
        matches_started=None,
        total_minutes=None,
        minutes_divided_90=None,
        goals_scored=None,
        assists=None,
        total_goal_assists=None,
        non_pk_goals=None,
        pk_made=None,
        pk_attempted=None,
        yellow_cards=None,
        red_cards=None,
        goal_value=None,
        gv_avg=None,
        goal_per_90=None,
        assists_per_90=None,
        total_goals_assists_per_90=None,
        non_pk_goals_per_90=None,
        non_pk_goal_and_assists_per_90=None,
    )


@pytest.fixture
def sample_season_display() -> SeasonDisplay:
    """Create a sample SeasonDisplay."""
    return SeasonDisplay(id=1, start_year=2023, end_year=None, display_name="2023-24")


@pytest.fixture
def sample_team_info() -> TeamInfo:
    """Create a sample TeamInfo."""
    return TeamInfo(id=1, name="Barcelona")


@pytest.fixture
def sample_competition_info() -> CompetitionInfo:
    """Create a sample CompetitionInfo."""
    return CompetitionInfo(id=1, name="La Liga")


@pytest.fixture
def sample_player_info() -> PlayerInfo:
    """Create a sample PlayerInfo."""
    return PlayerInfo(id=1, name="Lionel Messi", nation=None)


@pytest.fixture
def sample_nation_info() -> NationInfo:
    """Create a sample NationInfo."""
    return NationInfo(id=1, name="Argentina", country_code="AR")


@pytest.fixture
def sample_nation_basic() -> NationBasic:
    """Create a sample NationBasic."""
    return NationBasic(id=1, name="Argentina", country_code="AR")


@pytest.fixture
def sample_nation_detailed() -> NationDetailed:
    """Create a sample NationDetailed."""
    return NationDetailed(id=1, name="Argentina", country_code="AR")


@pytest.fixture
def empty_team_stats_info() -> TeamStatsInfo:
    """Create TeamStatsInfo with all None values."""
    return TeamStatsInfo(
        ranking=None,
        matches_played=None,
        wins=None,
        draws=None,
        losses=None,
        goals_for=None,
        goals_against=None,
        goal_difference=None,
        points=None,
        attendance=None,
        notes=None,
    )


@pytest.fixture
def sample_player_basic() -> PlayerBasic:
    """Create a sample PlayerBasic."""
    return PlayerBasic(id=1, name="Lionel Messi")
