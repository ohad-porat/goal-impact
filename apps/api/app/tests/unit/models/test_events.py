"""Unit tests for Event model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.tests.utils.factories import EventFactory, MatchFactory, PlayerFactory


class TestEventModel:
    """Test Event model functionality."""

    def test_create_event(self, db_session) -> None:
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
            player=player,
        )
        db_session.commit()

        assert event.id is not None
        assert event.event_type == "goal"
        assert event.minute == 45
        assert event.match_id == match.id
        assert event.player_id == player.id

    def test_event_unique_constraint(self, db_session) -> None:
        """Test unique constraint on (match_id, player_id, minute, event_type)."""
        match = MatchFactory()
        player = PlayerFactory()

        EventFactory(match=match, player=player, minute=10, event_type="goal")
        db_session.commit()

        with pytest.raises(IntegrityError):
            EventFactory(match=match, player=player, minute=10, event_type="goal")
            db_session.commit()

    def test_event_same_minute_different_type(self, db_session) -> None:
        """Test that same minute but different event_type is allowed."""
        match = MatchFactory()
        player = PlayerFactory()

        EventFactory(match=match, player=player, minute=10, event_type="goal")
        db_session.commit()

        event2 = EventFactory(match=match, player=player, minute=10, event_type="assist")
        db_session.commit()

        assert event2.id is not None

    def test_event_foreign_keys(self, db_session) -> None:
        """Test foreign key relationships."""
        match = MatchFactory()
        player = PlayerFactory()
        event = EventFactory(match=match, player=player)
        db_session.commit()

        assert event.match == match
        assert event.player == player

    def test_event_optional_fields(self, db_session) -> None:
        """Test that optional fields can be null."""
        event = EventFactory(xg=None, post_shot_xg=None, xg_difference=None, goal_value=None)
        db_session.commit()

        assert event.xg is None
        assert event.post_shot_xg is None
        assert event.xg_difference is None
        assert event.goal_value is None

    def test_event_relationships(self, db_session) -> None:
        """Test that reverse relationships work correctly."""
        match = MatchFactory()
        player = PlayerFactory()
        event = EventFactory(match=match, player=player)
        db_session.commit()

        assert event in match.events
        assert event in player.events

    def test_event_minute_validation_valid_range(self, db_session) -> None:
        """Test that minute can be between 0 and 120 (including stoppage time)."""
        match = MatchFactory()
        player = PlayerFactory()

        event1 = EventFactory(match=match, player=player, minute=0)
        event2 = EventFactory(match=match, player=player, minute=45)
        event3 = EventFactory(match=match, player=player, minute=90)
        event4 = EventFactory(match=match, player=player, minute=120)
        db_session.commit()

        assert event1.minute == 0
        assert event2.minute == 45
        assert event3.minute == 90
        assert event4.minute == 120

    def test_event_minute_validation_invalid_range(self, db_session) -> None:
        """Test that minute outside 0-120 range raises ValueError."""
        from app.models import Event

        match = MatchFactory()
        player = PlayerFactory()

        with pytest.raises(ValueError, match="Minute must be between 0 and 120"):
            Event(
                event_type="goal",
                minute=121,
                match_id=match.id,
                player_id=player.id,
            )

    def test_event_minute_validation_negative(self, db_session) -> None:
        """Test that negative minute raises ValueError."""
        from app.models import Event

        match = MatchFactory()
        player = PlayerFactory()

        with pytest.raises(ValueError, match="Minute must be between 0 and 120"):
            Event(
                event_type="goal",
                minute=-1,
                match_id=match.id,
                player_id=player.id,
            )

    def test_event_type_validation_valid_types(self, db_session) -> None:
        """Test that valid event types are accepted."""
        match = MatchFactory()
        player = PlayerFactory()

        goal = EventFactory(match=match, player=player, event_type="goal")
        own_goal = EventFactory(match=match, player=player, event_type="own goal")
        assist = EventFactory(match=match, player=player, event_type="assist")
        db_session.commit()

        assert goal.event_type == "goal"
        assert own_goal.event_type == "own goal"
        assert assist.event_type == "assist"

    def test_event_type_validation_invalid_type(self, db_session) -> None:
        """Test that invalid event types raise ValueError."""
        from app.models import Event

        match = MatchFactory()
        player = PlayerFactory()

        with pytest.raises(ValueError, match="Invalid event_type"):
            Event(
                event_type="yellow card",
                minute=10,
                match_id=match.id,
                player_id=player.id,
            )

    def test_event_type_validation_allows_none(self, db_session) -> None:
        """Test that event_type can be None."""
        match = MatchFactory()
        player = PlayerFactory()

        event = EventFactory(match=match, player=player, event_type=None)
        db_session.commit()

        assert event.event_type is None
