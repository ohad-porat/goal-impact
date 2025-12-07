"""Unit tests for leaders schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.common import NationInfo
from app.schemas.leaders import (
    BySeasonPlayer,
    BySeasonResponse,
    CareerTotalsPlayer,
    CareerTotalsResponse,
)


class TestCareerTotalsPlayer:
    """Test CareerTotalsPlayer schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating CareerTotalsPlayer with required fields."""
        player = CareerTotalsPlayer(
            player_id=1,
            player_name="Lionel Messi",
            nation=None,
            total_goal_value=100.5,
            goal_value_avg=1.25,
            total_goals=80,
            total_matches=90,
        )
        assert player.player_id == 1
        assert player.player_name == "Lionel Messi"
        assert player.total_goal_value == 100.5
        assert player.goal_value_avg == 1.25
        assert player.total_goals == 80
        assert player.total_matches == 90
        assert player.nation is None

    def test_creates_with_nation(self, sample_nation_info: NationInfo) -> None:
        """Test creating CareerTotalsPlayer with nation."""
        player = CareerTotalsPlayer(
            player_id=1,
            player_name="Lionel Messi",
            nation=sample_nation_info,
            total_goal_value=100.5,
            goal_value_avg=1.25,
            total_goals=80,
            total_matches=90,
        )
        assert player.nation is not None
        assert player.nation.id == 1

    def test_requires_player_id(self) -> None:
        """Test that player_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_name="Lionel Messi",
                total_goal_value=100.5,
                goal_value_avg=1.25,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_id",) for error in errors)

    def test_requires_player_name(self) -> None:
        """Test that player_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                total_goal_value=100.5,
                goal_value_avg=1.25,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_name",) for error in errors)

    def test_requires_total_goal_value(self) -> None:
        """Test that total_goal_value is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                player_name="Lionel Messi",
                goal_value_avg=1.25,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_goal_value",) for error in errors)

    def test_requires_goal_value_avg(self) -> None:
        """Test that goal_value_avg is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                player_name="Lionel Messi",
                total_goal_value=100.5,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goal_value_avg",) for error in errors)

    def test_requires_total_goals(self) -> None:
        """Test that total_goals is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                player_name="Lionel Messi",
                total_goal_value=100.5,
                goal_value_avg=1.25,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_goals",) for error in errors)

    def test_requires_total_matches(self) -> None:
        """Test that total_matches is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                player_name="Lionel Messi",
                total_goal_value=100.5,
                goal_value_avg=1.25,
                total_goals=80,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_matches",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id="not_int",
                player_name="Lionel Messi",
                total_goal_value=100.5,
                goal_value_avg=1.25,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                player_name=123,
                total_goal_value=100.5,
                goal_value_avg=1.25,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_name",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsPlayer(
                player_id=1,
                player_name="Lionel Messi",
                total_goal_value="not_float",
                goal_value_avg=1.25,
                total_goals=80,
                total_matches=90,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_goal_value",) for error in errors)

    def test_accepts_zero_values(self) -> None:
        """Test that zero is a valid value for numeric fields."""
        player = CareerTotalsPlayer(
            player_id=1,
            player_name="Lionel Messi",
            nation=None,
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_matches=0,
        )
        assert player.total_goal_value == 0.0
        assert player.total_goals == 0
        assert player.total_matches == 0

    def test_accepts_unicode_in_names(self) -> None:
        """Test that player names with unicode characters work."""
        player = CareerTotalsPlayer(
            player_id=1,
            player_name="José Mourinho",
            nation=None,
            total_goal_value=50.0,
            goal_value_avg=1.0,
            total_goals=40,
            total_matches=50,
        )
        assert player.player_name == "José Mourinho"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = CareerTotalsPlayer(
            player_id=1,
            player_name="Lionel Messi",
            nation=None,
            total_goal_value=100.5,
            goal_value_avg=1.25,
            total_goals=80,
            total_matches=90,
        )
        data = player.model_dump()
        assert data["player_id"] == 1
        assert data["player_name"] == "Lionel Messi"
        assert data["total_goal_value"] == 100.5

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "player_id": 1,
            "player_name": "Lionel Messi",
            "nation": None,
            "total_goal_value": 100.5,
            "goal_value_avg": 1.25,
            "total_goals": 80,
            "total_matches": 90,
        }
        player = CareerTotalsPlayer.model_validate(data)
        assert player.player_id == 1
        assert player.player_name == "Lionel Messi"
        assert player.total_goal_value == 100.5


class TestCareerTotalsResponse:
    """Test CareerTotalsResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating CareerTotalsResponse with empty list."""
        response = CareerTotalsResponse(top_goal_value=[])
        assert response.top_goal_value == []

    def test_creates_with_players(self) -> None:
        """Test creating CareerTotalsResponse with players."""
        player1 = CareerTotalsPlayer(
            player_id=1,
            player_name="Lionel Messi",
            nation=None,
            total_goal_value=100.5,
            goal_value_avg=1.25,
            total_goals=80,
            total_matches=90,
        )
        player2 = CareerTotalsPlayer(
            player_id=2,
            player_name="Cristiano Ronaldo",
            nation=None,
            total_goal_value=95.0,
            goal_value_avg=1.20,
            total_goals=75,
            total_matches=85,
        )
        response = CareerTotalsResponse(top_goal_value=[player1, player2])
        assert len(response.top_goal_value) == 2
        assert response.top_goal_value[0].player_name == "Lionel Messi"
        assert response.top_goal_value[1].player_name == "Cristiano Ronaldo"

    def test_requires_top_goal_value(self) -> None:
        """Test that top_goal_value is required."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("top_goal_value",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that top_goal_value must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            CareerTotalsResponse(top_goal_value="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("top_goal_value",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = CareerTotalsPlayer(
            player_id=1,
            player_name="Lionel Messi",
            nation=None,
            total_goal_value=100.5,
            goal_value_avg=1.25,
            total_goals=80,
            total_matches=90,
        )
        response = CareerTotalsResponse(top_goal_value=[player])
        data = response.model_dump()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "top_goal_value": [
                {
                    "player_id": 1,
                    "player_name": "Lionel Messi",
                    "nation": None,
                    "total_goal_value": 100.5,
                    "goal_value_avg": 1.25,
                    "total_goals": 80,
                    "total_matches": 90,
                }
            ]
        }
        response = CareerTotalsResponse.model_validate(data)
        assert len(response.top_goal_value) == 1
        assert response.top_goal_value[0].player_name == "Lionel Messi"


class TestBySeasonPlayer:
    """Test BySeasonPlayer schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating BySeasonPlayer with required fields."""
        player = BySeasonPlayer(
            player_id=1,
            player_name="Lionel Messi",
            clubs="Barcelona",
            total_goal_value=50.5,
            goal_value_avg=1.25,
            total_goals=40,
            total_matches=45,
        )
        assert player.player_id == 1
        assert player.player_name == "Lionel Messi"
        assert player.clubs == "Barcelona"
        assert player.total_goal_value == 50.5
        assert player.goal_value_avg == 1.25
        assert player.total_goals == 40
        assert player.total_matches == 45

    def test_requires_player_id(self) -> None:
        """Test that player_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            BySeasonPlayer(
                player_name="Lionel Messi",
                clubs="Barcelona",
                total_goal_value=50.5,
                goal_value_avg=1.25,
                total_goals=40,
                total_matches=45,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_id",) for error in errors)

    def test_requires_player_name(self) -> None:
        """Test that player_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            BySeasonPlayer(
                player_id=1,
                clubs="Barcelona",
                total_goal_value=50.5,
                goal_value_avg=1.25,
                total_goals=40,
                total_matches=45,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_name",) for error in errors)

    def test_requires_clubs(self) -> None:
        """Test that clubs is required."""
        with pytest.raises(ValidationError) as exc_info:
            BySeasonPlayer(
                player_id=1,
                player_name="Lionel Messi",
                total_goal_value=50.5,
                goal_value_avg=1.25,
                total_goals=40,
                total_matches=45,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("clubs",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            BySeasonPlayer(
                player_id="not_int",
                player_name="Lionel Messi",
                clubs="Barcelona",
                total_goal_value=50.5,
                goal_value_avg=1.25,
                total_goals=40,
                total_matches=45,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            BySeasonPlayer(
                player_id=1,
                player_name=123,
                clubs="Barcelona",
                total_goal_value=50.5,
                goal_value_avg=1.25,
                total_goals=40,
                total_matches=45,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_name",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            BySeasonPlayer(
                player_id=1,
                player_name="Lionel Messi",
                clubs=123,
                total_goal_value=50.5,
                goal_value_avg=1.25,
                total_goals=40,
                total_matches=45,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("clubs",) for error in errors)

    def test_accepts_zero_values(self) -> None:
        """Test that zero is a valid value for numeric fields."""
        player = BySeasonPlayer(
            player_id=1,
            player_name="Lionel Messi",
            clubs="Barcelona",
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_matches=0,
        )
        assert player.total_goal_value == 0.0
        assert player.total_goals == 0
        assert player.total_matches == 0

    def test_accepts_unicode_in_names(self) -> None:
        """Test that player names with unicode characters work."""
        player = BySeasonPlayer(
            player_id=1,
            player_name="José Mourinho",
            clubs="Barcelona",
            total_goal_value=50.0,
            goal_value_avg=1.0,
            total_goals=40,
            total_matches=50,
        )
        assert player.player_name == "José Mourinho"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = BySeasonPlayer(
            player_id=1,
            player_name="Lionel Messi",
            clubs="Barcelona",
            total_goal_value=50.5,
            goal_value_avg=1.25,
            total_goals=40,
            total_matches=45,
        )
        data = player.model_dump()
        assert data["player_id"] == 1
        assert data["player_name"] == "Lionel Messi"
        assert data["clubs"] == "Barcelona"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "player_id": 1,
            "player_name": "Lionel Messi",
            "clubs": "Barcelona",
            "total_goal_value": 50.5,
            "goal_value_avg": 1.25,
            "total_goals": 40,
            "total_matches": 45,
        }
        player = BySeasonPlayer.model_validate(data)
        assert player.player_id == 1
        assert player.player_name == "Lionel Messi"
        assert player.clubs == "Barcelona"


class TestBySeasonResponse:
    """Test BySeasonResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating BySeasonResponse with empty list."""
        response = BySeasonResponse(top_goal_value=[])
        assert response.top_goal_value == []

    def test_creates_with_players(self) -> None:
        """Test creating BySeasonResponse with players."""
        player1 = BySeasonPlayer(
            player_id=1,
            player_name="Lionel Messi",
            clubs="Barcelona",
            total_goal_value=50.5,
            goal_value_avg=1.25,
            total_goals=40,
            total_matches=45,
        )
        player2 = BySeasonPlayer(
            player_id=2,
            player_name="Cristiano Ronaldo",
            clubs="Real Madrid",
            total_goal_value=45.0,
            goal_value_avg=1.20,
            total_goals=35,
            total_matches=40,
        )
        response = BySeasonResponse(top_goal_value=[player1, player2])
        assert len(response.top_goal_value) == 2
        assert response.top_goal_value[0].player_name == "Lionel Messi"
        assert response.top_goal_value[1].player_name == "Cristiano Ronaldo"

    def test_requires_top_goal_value(self) -> None:
        """Test that top_goal_value is required."""
        with pytest.raises(ValidationError) as exc_info:
            BySeasonResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("top_goal_value",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that top_goal_value must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            BySeasonResponse(top_goal_value="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("top_goal_value",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = BySeasonPlayer(
            player_id=1,
            player_name="Lionel Messi",
            clubs="Barcelona",
            total_goal_value=50.5,
            goal_value_avg=1.25,
            total_goals=40,
            total_matches=45,
        )
        response = BySeasonResponse(top_goal_value=[player])
        data = response.model_dump()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "top_goal_value": [
                {
                    "player_id": 1,
                    "player_name": "Lionel Messi",
                    "clubs": "Barcelona",
                    "total_goal_value": 50.5,
                    "goal_value_avg": 1.25,
                    "total_goals": 40,
                    "total_matches": 45,
                }
            ]
        }
        response = BySeasonResponse.model_validate(data)
        assert len(response.top_goal_value) == 1
        assert response.top_goal_value[0].player_name == "Lionel Messi"
