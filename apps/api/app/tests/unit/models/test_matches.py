"""Unit tests for Match model."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Match
from app.tests.utils.factories import MatchFactory, SeasonFactory, TeamFactory


class TestMatchModel:
    """Test Match model functionality."""

    def test_create_match(self, db_session):
        """Test creating a match with all fields."""
        season = SeasonFactory()
        home_team = TeamFactory()
        away_team = TeamFactory()

        match = MatchFactory(
            home_team_goals=2,
            away_team_goals=1,
            date=date(2024, 1, 15),
            fbref_id="abc123",
            fbref_url="/en/matches/abc123/",
            season=season,
            home_team=home_team,
            away_team=away_team,
        )
        db_session.commit()

        assert match.id is not None
        assert match.home_team_goals == 2
        assert match.away_team_goals == 1
        assert match.date == date(2024, 1, 15)
        assert match.season_id == season.id
        assert match.home_team_id == home_team.id
        assert match.away_team_id == away_team.id

    def test_match_unique_fbref_id(self, db_session):
        """Test that fbref_id must be unique."""
        MatchFactory(fbref_id="abc123", fbref_url="/en/matches/abc123/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            MatchFactory(fbref_id="abc123", fbref_url="/en/matches/abc123-2/")
            db_session.commit()

    def test_match_unique_fbref_url(self, db_session):
        """Test that fbref_url must be unique."""
        MatchFactory(fbref_id="abc123", fbref_url="/en/matches/abc123/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            MatchFactory(fbref_id="abc124", fbref_url="/en/matches/abc123/")
            db_session.commit()

    def test_match_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            match = Match(home_team_goals=2, away_team_goals=1)
            db_session.add(match)
            db_session.commit()

    def test_match_foreign_keys(self, db_session):
        """Test foreign key relationships."""
        season = SeasonFactory()
        home_team = TeamFactory()
        away_team = TeamFactory()
        match = MatchFactory(season=season, home_team=home_team, away_team=away_team)
        db_session.commit()

        assert match.season == season
        assert match.home_team == home_team
        assert match.away_team == away_team

    def test_match_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        match = MatchFactory(home_team_goals=None, away_team_goals=None, date=None)
        db_session.commit()

        assert match.home_team_goals is None
        assert match.away_team_goals is None
        assert match.date is None

    def test_match_same_team_home_and_away(self, db_session):
        """Test that home_team and away_team can be the same."""
        team = TeamFactory()
        match = MatchFactory(home_team=team, away_team=team)
        db_session.commit()

        assert match.home_team_id == match.away_team_id
