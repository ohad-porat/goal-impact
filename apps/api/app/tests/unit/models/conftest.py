"""Model-specific pytest fixtures."""

import pytest

from app.tests.utils.factories import (
    NationFactory, CompetitionFactory, SeasonFactory, TeamFactory,
    PlayerFactory, MatchFactory, EventFactory, PlayerStatsFactory,
    TeamStatsFactory, GoalValueLookupFactory, StatsCalculationMetadataFactory
)


@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """Set up factory-boy to use the test database session."""
    for factory_class in [
        NationFactory, CompetitionFactory, SeasonFactory, TeamFactory,
        PlayerFactory, MatchFactory, EventFactory, PlayerStatsFactory,
        TeamStatsFactory, GoalValueLookupFactory, StatsCalculationMetadataFactory
    ]:
        factory_class._meta.sqlalchemy_session = db_session
    
    yield
    
    for factory_class in [
        NationFactory, CompetitionFactory, SeasonFactory, TeamFactory,
        PlayerFactory, MatchFactory, EventFactory, PlayerStatsFactory,
        TeamStatsFactory, GoalValueLookupFactory, StatsCalculationMetadataFactory
    ]:
        factory_class._meta.sqlalchemy_session = None
