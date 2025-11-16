"""Unit tests for Event model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Event
from app.tests.utils.factories import (
    EventFactory, MatchFactory, PlayerFactory
)


class TestEventModel:
    """Test Event model functionality."""

    def test_create_event(self, db_session):
        """Test creating an event with all fields."""
        match = MatchFactory()
        player = PlayerFactory()
        
        event = EventFactory(
            event_type="goal",
            minute=45,
            home_team_goals_pre_event=1,
            away_team_goals_pre_event=0,
            home_team_goals_post_event=2,
            away_team_goals_post_event=0,
            match=match,
            player=player
        )
        db_session.commit()
        
        assert event.id is not None
        assert event.event_type == "goal"
        assert event.minute == 45
        assert event.match_id == match.id
        assert event.player_id == player.id

    def test_event_unique_constraint(self, db_session):
        """Test unique constraint on (match_id, player_id, minute, event_type)."""
        match = MatchFactory()
        player = PlayerFactory()
        
        EventFactory(
            match=match,
            player=player,
            minute=10,
            event_type="goal"
        )
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            EventFactory(
                match=match,
                player=player,
                minute=10,
                event_type="goal"
            )
            db_session.commit()

    def test_event_same_minute_different_type(self, db_session):
        """Test that same minute but different event_type is allowed."""
        match = MatchFactory()
        player = PlayerFactory()
        
        EventFactory(
            match=match,
            player=player,
            minute=10,
            event_type="goal"
        )
        db_session.commit()
        
        event2 = EventFactory(
            match=match,
            player=player,
            minute=10,
            event_type="assist"
        )
        db_session.commit()
        
        assert event2.id is not None

    def test_event_foreign_keys(self, db_session):
        """Test foreign key relationships."""
        match = MatchFactory()
        player = PlayerFactory()
        event = EventFactory(match=match, player=player)
        db_session.commit()
        
        assert event.match == match
        assert event.player == player

    def test_event_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        event = EventFactory(
            xg=None,
            post_shot_xg=None,
            xg_difference=None,
            goal_value=None
        )
        db_session.commit()
        
        assert event.xg is None
        assert event.post_shot_xg is None
        assert event.xg_difference is None
        assert event.goal_value is None

    def test_event_relationships(self, db_session):
        """Test that reverse relationships work correctly."""
        match = MatchFactory()
        player = PlayerFactory()
        event = EventFactory(match=match, player=player)
        db_session.commit()
        
        assert event in match.events
        assert event in player.events
