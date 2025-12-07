"""Unit tests for nations schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.clubs import ClubSummary
from app.schemas.nations import (
    CompetitionSummary,
    NationDetails,
    NationDetailsResponse,
    NationSummary,
    NationsListResponse,
    PlayerSummary,
)


class TestNationSummary:
    """Test NationSummary schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating NationSummary with required fields."""
        nation = NationSummary(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
            player_count=50,
        )
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"
        assert nation.governing_body == "AFA"
        assert nation.player_count == 50

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                name="Argentina",
                country_code="AR",
                governing_body="AFA",
                player_count=50,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id=1,
                country_code="AR",
                governing_body="AFA",
                player_count=50,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_country_code(self) -> None:
        """Test that country_code is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id=1,
                name="Argentina",
                governing_body="AFA",
                player_count=50,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country_code",) for error in errors)

    def test_requires_governing_body(self) -> None:
        """Test that governing_body is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id=1,
                name="Argentina",
                country_code="AR",
                player_count=50,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("governing_body",) for error in errors)

    def test_requires_player_count(self) -> None:
        """Test that player_count is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id=1,
                name="Argentina",
                country_code="AR",
                governing_body="AFA",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_count",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id="not_int",
                name="Argentina",
                country_code="AR",
                governing_body="AFA",
                player_count=50,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id=1,
                name=123,
                country_code="AR",
                governing_body="AFA",
                player_count=50,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationSummary(
                id=1,
                name="Argentina",
                country_code="AR",
                governing_body="AFA",
                player_count="not_int",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player_count",) for error in errors)

    def test_accepts_zero_player_count(self) -> None:
        """Test that zero is a valid value for player_count."""
        nation = NationSummary(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
            player_count=0,
        )
        assert nation.player_count == 0

    def test_accepts_unicode_in_names(self) -> None:
        """Test that nation names with unicode characters work."""
        nation = NationSummary(
            id=1,
            name="Côte d'Ivoire",
            country_code="CI",
            governing_body="FIF",
            player_count=30,
        )
        assert nation.name == "Côte d'Ivoire"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationSummary(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
            player_count=50,
        )
        data = nation.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Argentina"
        assert data["player_count"] == 50

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": 1,
            "name": "Argentina",
            "country_code": "AR",
            "governing_body": "AFA",
            "player_count": 50,
        }
        nation = NationSummary.model_validate(data)
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.player_count == 50


class TestNationsListResponse:
    """Test NationsListResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating NationsListResponse with empty list."""
        response = NationsListResponse(nations=[])
        assert response.nations == []

    def test_creates_with_nations(self) -> None:
        """Test creating NationsListResponse with nations."""
        nation1 = NationSummary(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
            player_count=50,
        )
        nation2 = NationSummary(
            id=2,
            name="Brazil",
            country_code="BR",
            governing_body="CBF",
            player_count=60,
        )
        response = NationsListResponse(nations=[nation1, nation2])
        assert len(response.nations) == 2
        assert response.nations[0].name == "Argentina"
        assert response.nations[1].name == "Brazil"

    def test_requires_nations(self) -> None:
        """Test that nations is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationsListResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nations",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that nations must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            NationsListResponse(nations="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nations",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationSummary(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
            player_count=50,
        )
        response = NationsListResponse(nations=[nation])
        data = response.model_dump()
        assert len(data["nations"]) == 1
        assert data["nations"][0]["name"] == "Argentina"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "nations": [
                {
                    "id": 1,
                    "name": "Argentina",
                    "country_code": "AR",
                    "governing_body": "AFA",
                    "player_count": 50,
                }
            ]
        }
        response = NationsListResponse.model_validate(data)
        assert len(response.nations) == 1
        assert response.nations[0].name == "Argentina"


class TestNationDetails:
    """Test NationDetails schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating NationDetails with required fields."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"
        assert nation.governing_body == "AFA"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetails(name="Argentina", country_code="AR", governing_body="AFA")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetails(id=1, country_code="AR", governing_body="AFA")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_country_code(self) -> None:
        """Test that country_code is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetails(id=1, name="Argentina", governing_body="AFA")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country_code",) for error in errors)

    def test_requires_governing_body(self) -> None:
        """Test that governing_body is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetails(id=1, name="Argentina", country_code="AR")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("governing_body",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetails(id="not_int", name="Argentina", country_code="AR", governing_body="AFA")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationDetails(id=1, name=123, country_code="AR", governing_body="AFA")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        data = nation.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Argentina"
        assert data["governing_body"] == "AFA"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": 1,
            "name": "Argentina",
            "country_code": "AR",
            "governing_body": "AFA",
        }
        nation = NationDetails.model_validate(data)
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.governing_body == "AFA"


class TestCompetitionSummary:
    """Test CompetitionSummary schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating CompetitionSummary with required fields."""
        competition = CompetitionSummary(
            id=1, name="La Liga", tier=None, season_count=5, has_seasons=True
        )
        assert competition.id == 1
        assert competition.name == "La Liga"
        assert competition.season_count == 5
        assert competition.has_seasons is True
        assert competition.tier is None

    def test_creates_with_tier(self) -> None:
        """Test creating CompetitionSummary with tier."""
        competition = CompetitionSummary(
            id=1,
            name="La Liga",
            tier="1",
            season_count=5,
            has_seasons=True,
        )
        assert competition.tier == "1"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(name="La Liga", season_count=5, has_seasons=True)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(id=1, season_count=5, has_seasons=True)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_season_count(self) -> None:
        """Test that season_count is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(id=1, name="La Liga", has_seasons=True)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season_count",) for error in errors)

    def test_requires_has_seasons(self) -> None:
        """Test that has_seasons is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(id=1, name="La Liga", season_count=5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("has_seasons",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(
                id="not_int",
                name="La Liga",
                season_count=5,
                has_seasons=True,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(
                id=1,
                name=123,
                season_count=5,
                has_seasons=True,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(
                id=1,
                name="La Liga",
                season_count="not_int",
                has_seasons=True,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season_count",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CompetitionSummary(
                id=1,
                name="La Liga",
                season_count=5,
                has_seasons="not_bool",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("has_seasons",) for error in errors)

    def test_accepts_zero_season_count(self) -> None:
        """Test that zero is a valid value for season_count."""
        competition = CompetitionSummary(
            id=1, name="La Liga", tier=None, season_count=0, has_seasons=False
        )
        assert competition.season_count == 0
        assert competition.has_seasons is False

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        competition = CompetitionSummary(
            id=1, name="La Liga", tier="1", season_count=5, has_seasons=True
        )
        data = competition.model_dump()
        assert data["id"] == 1
        assert data["name"] == "La Liga"
        assert data["season_count"] == 5
        assert data["has_seasons"] is True

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": 1,
            "name": "La Liga",
            "tier": "1",
            "season_count": 5,
            "has_seasons": True,
        }
        competition = CompetitionSummary.model_validate(data)
        assert competition.id == 1
        assert competition.name == "La Liga"
        assert competition.season_count == 5


class TestPlayerSummary:
    """Test PlayerSummary schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating PlayerSummary with required fields."""
        player = PlayerSummary(id=1, name="Lionel Messi", total_goal_value=100.5)
        assert player.id == 1
        assert player.name == "Lionel Messi"
        assert player.total_goal_value == 100.5

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerSummary(name="Lionel Messi", total_goal_value=100.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerSummary(id=1, total_goal_value=100.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_total_goal_value(self) -> None:
        """Test that total_goal_value is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerSummary(id=1, name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_goal_value",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerSummary(id="not_int", name="Lionel Messi", total_goal_value=100.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            PlayerSummary(id=1, name=123, total_goal_value=100.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            PlayerSummary(id=1, name="Lionel Messi", total_goal_value="not_float")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_goal_value",) for error in errors)

    def test_accepts_zero_goal_value(self) -> None:
        """Test that zero is a valid value for total_goal_value."""
        player = PlayerSummary(id=1, name="Lionel Messi", total_goal_value=0.0)
        assert player.total_goal_value == 0.0

    def test_accepts_unicode_in_names(self) -> None:
        """Test that player names with unicode characters work."""
        player = PlayerSummary(id=1, name="José Mourinho", total_goal_value=50.0)
        assert player.name == "José Mourinho"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = PlayerSummary(id=1, name="Lionel Messi", total_goal_value=100.5)
        data = player.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Lionel Messi"
        assert data["total_goal_value"] == 100.5

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Lionel Messi", "total_goal_value": 100.5}
        player = PlayerSummary.model_validate(data)
        assert player.id == 1
        assert player.name == "Lionel Messi"
        assert player.total_goal_value == 100.5


class TestNationDetailsResponse:
    """Test NationDetailsResponse schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating NationDetailsResponse with required fields."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        competition = CompetitionSummary(
            id=1, name="La Liga", tier=None, season_count=5, has_seasons=True
        )
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        player = PlayerSummary(id=1, name="Lionel Messi", total_goal_value=100.5)

        response = NationDetailsResponse(
            nation=nation,
            competitions=[competition],
            clubs=[club],
            players=[player],
        )

        assert response.nation.name == "Argentina"
        assert len(response.competitions) == 1
        assert len(response.clubs) == 1
        assert len(response.players) == 1

    def test_creates_with_empty_lists(self) -> None:
        """Test creating NationDetailsResponse with empty lists."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        response = NationDetailsResponse(
            nation=nation,
            competitions=[],
            clubs=[],
            players=[],
        )
        assert response.competitions == []
        assert response.clubs == []
        assert response.players == []

    def test_requires_nation(self) -> None:
        """Test that nation is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(competitions=[], clubs=[], players=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nation",) for error in errors)

    def test_requires_competitions(self) -> None:
        """Test that competitions is required."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(nation=nation, clubs=[], players=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("competitions",) for error in errors)

    def test_requires_clubs(self) -> None:
        """Test that clubs is required."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(nation=nation, competitions=[], players=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("clubs",) for error in errors)

    def test_requires_players(self) -> None:
        """Test that players is required."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(nation=nation, competitions=[], clubs=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("players",) for error in errors)

    def test_validates_list_types(self) -> None:
        """Test that list types are validated."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(
                nation=nation,
                competitions="not_a_list",
                clubs=[],
                players=[],
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("competitions",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(
                nation=nation,
                competitions=[],
                clubs="not_a_list",
                players=[],
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("clubs",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationDetailsResponse(
                nation=nation,
                competitions=[],
                clubs=[],
                players="not_a_list",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("players",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationDetails(
            id=1,
            name="Argentina",
            country_code="AR",
            governing_body="AFA",
        )
        response = NationDetailsResponse(
            nation=nation,
            competitions=[],
            clubs=[],
            players=[],
        )
        data = response.model_dump()
        assert data["nation"]["name"] == "Argentina"
        assert data["competitions"] == []
        assert data["clubs"] == []

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "nation": {
                "id": 1,
                "name": "Argentina",
                "country_code": "AR",
                "governing_body": "AFA",
            },
            "competitions": [],
            "clubs": [],
            "players": [],
        }
        response = NationDetailsResponse.model_validate(data)
        assert response.nation.name == "Argentina"
        assert response.competitions == []
