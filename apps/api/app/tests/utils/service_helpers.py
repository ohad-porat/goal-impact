"""Shared test helpers for service layer tests."""

from app.tests.utils.factories import (
    NationFactory,
    CompetitionFactory,
    SeasonFactory,
    TeamFactory,
    MatchFactory,
)


def create_match_with_teams(db_session, home_team_name=None, away_team_name=None, **match_kwargs):
    """Create a match with home and away teams."""
    home_team = TeamFactory(name=home_team_name) if home_team_name else TeamFactory()
    away_team = TeamFactory(name=away_team_name) if away_team_name else TeamFactory()
    match = MatchFactory(home_team=home_team, away_team=away_team, **match_kwargs)
    db_session.commit()
    return home_team, away_team, match


def create_basic_season_setup(db_session, nation=None, comp_name="Premier League", 
                              tier="1st", start_year=2023, end_year=2024):
    """Create a basic season setup (nation, competition, season)."""
    if nation is None:
        nation = NationFactory()
    comp = CompetitionFactory(name=comp_name, tier=tier, nation=nation)
    season = SeasonFactory(competition=comp, start_year=start_year, end_year=end_year)
    db_session.commit()
    return nation, comp, season
