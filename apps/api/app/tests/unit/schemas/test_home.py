"""Unit tests for home schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.home import (
    RecentGoalMatch,
    RecentGoalPlayer,
    RecentImpactGoal,
    RecentImpactGoalsResponse,
)


class TestRecentGoalPlayer:
    """Test RecentGoalPlayer schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating RecentGoalPlayer with required fields."""
        player = RecentGoalPlayer(id=1, name="Lionel Messi")
        assert player.id == 1
        assert player.name == "Lionel Messi"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalPlayer(name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalPlayer(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalPlayer(id="not_int", name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            RecentGoalPlayer(id=1, name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that player names with unicode characters work."""
        player = RecentGoalPlayer(id=1, name="José Mourinho")
        assert player.name == "José Mourinho"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = RecentGoalPlayer(id=1, name="Lionel Messi")
        data = player.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Lionel Messi"}
        player = RecentGoalPlayer.model_validate(data)
        assert player.id == 1
        assert player.name == "Lionel Messi"


class TestRecentGoalMatch:
    """Test RecentGoalMatch schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating RecentGoalMatch with required fields."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        assert match.home_team == "Barcelona"
        assert match.away_team == "Real Madrid"
        assert match.date == "2024-01-15"

    def test_requires_home_team(self) -> None:
        """Test that home_team is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalMatch(away_team="Real Madrid", date="2024-01-15")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("home_team",) for error in errors)

    def test_requires_away_team(self) -> None:
        """Test that away_team is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalMatch(home_team="Barcelona", date="2024-01-15")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("away_team",) for error in errors)

    def test_requires_date(self) -> None:
        """Test that date is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("date",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            RecentGoalMatch(home_team=123, away_team="Real Madrid", date="2024-01-15")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("home_team",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            RecentGoalMatch(home_team="Barcelona", away_team=123, date="2024-01-15")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("away_team",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("date",) for error in errors)

    def test_accepts_unicode_in_team_names(self) -> None:
        """Test that team names with unicode characters work."""
        match = RecentGoalMatch(home_team="São Paulo", away_team="Barcelona", date="2024-01-15")
        assert match.home_team == "São Paulo"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        data = match.model_dump()
        assert data["home_team"] == "Barcelona"
        assert data["away_team"] == "Real Madrid"
        assert data["date"] == "2024-01-15"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"home_team": "Barcelona", "away_team": "Real Madrid", "date": "2024-01-15"}
        match = RecentGoalMatch.model_validate(data)
        assert match.home_team == "Barcelona"
        assert match.away_team == "Real Madrid"
        assert match.date == "2024-01-15"


class TestRecentImpactGoal:
    """Test RecentImpactGoal schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating RecentImpactGoal with required fields."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        goal = RecentImpactGoal(
            match=match,
            scorer=scorer,
            minute=45,
            goal_value=2.5,
            score_before="1-0",
            score_after="2-0",
        )
        assert goal.match.home_team == "Barcelona"
        assert goal.scorer.name == "Lionel Messi"
        assert goal.minute == 45
        assert goal.goal_value == 2.5
        assert goal.score_before == "1-0"
        assert goal.score_after == "2-0"

    def test_requires_match(self) -> None:
        """Test that match is required."""
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                scorer=scorer,
                minute=45,
                goal_value=2.5,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("match",) for error in errors)

    def test_requires_scorer(self) -> None:
        """Test that scorer is required."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                minute=45,
                goal_value=2.5,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("scorer",) for error in errors)

    def test_requires_minute(self) -> None:
        """Test that minute is required."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                scorer=scorer,
                goal_value=2.5,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("minute",) for error in errors)

    def test_requires_goal_value(self) -> None:
        """Test that goal_value is required."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                scorer=scorer,
                minute=45,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goal_value",) for error in errors)

    def test_requires_score_before(self) -> None:
        """Test that score_before is required."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                scorer=scorer,
                minute=45,
                goal_value=2.5,
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("score_before",) for error in errors)

    def test_requires_score_after(self) -> None:
        """Test that score_after is required."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                scorer=scorer,
                minute=45,
                goal_value=2.5,
                score_before="1-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("score_after",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                scorer=scorer,
                minute="not_int",
                goal_value=2.5,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("minute",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoal(
                match=match,
                scorer=scorer,
                minute=45,
                goal_value="not_float",
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goal_value",) for error in errors)

    def test_accepts_zero_minute(self) -> None:
        """Test that zero is a valid value for minute."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        goal = RecentImpactGoal(
            match=match,
            scorer=scorer,
            minute=0,
            goal_value=2.5,
            score_before="0-0",
            score_after="1-0",
        )
        assert goal.minute == 0

    def test_accepts_zero_goal_value(self) -> None:
        """Test that zero is a valid value for goal_value."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        goal = RecentImpactGoal(
            match=match,
            scorer=scorer,
            minute=45,
            goal_value=0.0,
            score_before="1-0",
            score_after="2-0",
        )
        assert goal.goal_value == 0.0

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        goal = RecentImpactGoal(
            match=match,
            scorer=scorer,
            minute=45,
            goal_value=2.5,
            score_before="1-0",
            score_after="2-0",
        )
        data = goal.model_dump()
        assert data["minute"] == 45
        assert data["goal_value"] == 2.5
        assert data["scorer"]["name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "match": {"home_team": "Barcelona", "away_team": "Real Madrid", "date": "2024-01-15"},
            "scorer": {"id": 1, "name": "Lionel Messi"},
            "minute": 45,
            "goal_value": 2.5,
            "score_before": "1-0",
            "score_after": "2-0",
        }
        goal = RecentImpactGoal.model_validate(data)
        assert goal.minute == 45
        assert goal.goal_value == 2.5
        assert goal.scorer.name == "Lionel Messi"


class TestRecentImpactGoalsResponse:
    """Test RecentImpactGoalsResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating RecentImpactGoalsResponse with empty list."""
        response = RecentImpactGoalsResponse(goals=[])
        assert response.goals == []

    def test_creates_with_goals(self) -> None:
        """Test creating RecentImpactGoalsResponse with goals."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        goal = RecentImpactGoal(
            match=match,
            scorer=scorer,
            minute=45,
            goal_value=2.5,
            score_before="1-0",
            score_after="2-0",
        )
        response = RecentImpactGoalsResponse(goals=[goal])
        assert len(response.goals) == 1
        assert response.goals[0].scorer.name == "Lionel Messi"

    def test_requires_goals(self) -> None:
        """Test that goals is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoalsResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goals",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that goals must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            RecentImpactGoalsResponse(goals="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goals",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        match = RecentGoalMatch(home_team="Barcelona", away_team="Real Madrid", date="2024-01-15")
        scorer = RecentGoalPlayer(id=1, name="Lionel Messi")
        goal = RecentImpactGoal(
            match=match,
            scorer=scorer,
            minute=45,
            goal_value=2.5,
            score_before="1-0",
            score_after="2-0",
        )
        response = RecentImpactGoalsResponse(goals=[goal])
        data = response.model_dump()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["scorer"]["name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "goals": [
                {
                    "match": {
                        "home_team": "Barcelona",
                        "away_team": "Real Madrid",
                        "date": "2024-01-15",
                    },
                    "scorer": {"id": 1, "name": "Lionel Messi"},
                    "minute": 45,
                    "goal_value": 2.5,
                    "score_before": "1-0",
                    "score_after": "2-0",
                }
            ]
        }
        response = RecentImpactGoalsResponse.model_validate(data)
        assert len(response.goals) == 1
        assert response.goals[0].scorer.name == "Lionel Messi"
