"""Unit tests for TeamStats model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import TeamStats
from app.tests.utils.factories import (
    TeamStatsFactory, TeamFactory, SeasonFactory
)


class TestTeamStatsModel:
    """Test TeamStats model functionality."""

    def test_create_team_stats(self, db_session):
        """Test creating team stats with all fields."""
        team = TeamFactory()
        season = SeasonFactory()
        
        stats = TeamStatsFactory(
            team=team,
            season=season,
            ranking=1,
            matches_played=38,
            wins=30,
            draws=5,
            losses=3,
            goals_for=90,
            goals_against=30
        )
        db_session.commit()
        
        assert stats.id is not None
        assert stats.team_id == team.id
        assert stats.season_id == season.id
        assert stats.ranking == 1
        assert stats.matches_played == 38
        assert stats.wins == 30

    def test_team_stats_unique_fbref_url(self, db_session):
        """Test that fbref_url must be unique."""
        TeamStatsFactory(fbref_url="/en/squads/team_1/stats/")
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            TeamStatsFactory(fbref_url="/en/squads/team_1/stats/")
            db_session.commit()

    def test_team_stats_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            stats = TeamStats(
                ranking=1,
                matches_played=38
            )
            db_session.add(stats)
            db_session.commit()

    def test_team_stats_foreign_keys(self, db_session):
        """Test foreign key relationships."""
        team = TeamFactory()
        season = SeasonFactory()
        stats = TeamStatsFactory(team=team, season=season)
        db_session.commit()
        
        assert stats.team == team
        assert stats.season == season

    def test_team_stats_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        stats = TeamStatsFactory(
            ranking=None,
            goal_logs_url=None,
            notes=None,
            attendance=None
        )
        db_session.commit()
        
        assert stats.ranking is None
        assert stats.goal_logs_url is None
        assert stats.notes is None
        assert stats.attendance is None

    def test_team_stats_relationships(self, db_session):
        """Test that reverse relationships work correctly."""
        team = TeamFactory()
        season = SeasonFactory()
        stats = TeamStatsFactory(team=team, season=season)
        db_session.commit()
        
        assert stats in team.team_stats
        assert stats in season.team_stats
