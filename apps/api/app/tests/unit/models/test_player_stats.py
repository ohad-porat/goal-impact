"""Unit tests for PlayerStats model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import PlayerStats
from app.tests.utils.factories import (
    PlayerStatsFactory, PlayerFactory, SeasonFactory, TeamFactory
)


class TestPlayerStatsModel:
    """Test PlayerStats model functionality."""

    def test_create_player_stats(self, db_session):
        """Test creating player stats with all fields."""
        player = PlayerFactory()
        season = SeasonFactory()
        team = TeamFactory()
        
        stats = PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            matches_played=38,
            goals_scored=20,
            assists=10
        )
        db_session.commit()
        
        assert stats.id is not None
        assert stats.player_id == player.id
        assert stats.season_id == season.id
        assert stats.team_id == team.id
        assert stats.matches_played == 38
        assert stats.goals_scored == 20
        assert stats.assists == 10

    def test_player_stats_unique_constraint(self, db_session):
        """Test unique constraint on (player_id, season_id, team_id)."""
        player = PlayerFactory()
        season = SeasonFactory()
        team = TeamFactory()
        
        PlayerStatsFactory(player=player, season=season, team=team)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            PlayerStatsFactory(player=player, season=season, team=team)
            db_session.commit()

    def test_player_stats_different_season_allowed(self, db_session):
        """Test that same player and team but different season is allowed."""
        player = PlayerFactory()
        team = TeamFactory()
        season1 = SeasonFactory()
        season2 = SeasonFactory()
        
        stats1 = PlayerStatsFactory(player=player, season=season1, team=team)
        db_session.commit()
        
        stats2 = PlayerStatsFactory(player=player, season=season2, team=team)
        db_session.commit()
        
        assert stats1.id != stats2.id
        assert stats1.season_id != stats2.season_id

    def test_player_stats_foreign_keys(self, db_session):
        """Test foreign key relationships."""
        player = PlayerFactory()
        season = SeasonFactory()
        team = TeamFactory()
        stats = PlayerStatsFactory(player=player, season=season, team=team)
        db_session.commit()
        
        assert stats.player == player
        assert stats.season == season
        assert stats.team == team

    def test_player_stats_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        stats = PlayerStatsFactory(
            matches_played=10,
            total_minutes=900,
            minutes_divided_90=10.0,
            goals_scored=5,
            assists=3,
            total_goal_assists=8,
            non_pk_goals=5,
            pk_made=0,
            pk_attempted=0,
            yellow_cards=2,
            red_cards=0,
            xg=0.0,
            non_pk_xg=0.0,
            xag=0.0,
            npxg_and_xag=0.0,
            goal_value=None,
            gv_avg=None
        )
        db_session.commit()
        
        stats.goal_value = None
        stats.gv_avg = None
        db_session.commit()
        
        assert stats.goal_value is None
        assert stats.gv_avg is None
