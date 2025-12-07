"""Unit tests for leagues schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.leagues import (
    LeagueInfo,
    LeagueSeasonsResponse,
    LeagueSummary,
    LeagueTableEntry,
    LeagueTableResponse,
    LeaguesListResponse,
)
from app.schemas.players import SeasonDisplay


class TestLeagueSummary:
    """Test LeagueSummary schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating LeagueSummary with required fields."""
        league = LeagueSummary(
            id=1,
            name="La Liga",
            country="Spain",
            gender=None,
            tier=None,
            available_seasons="2023-24, 2024-25",
        )
        assert league.id == 1
        assert league.name == "La Liga"
        assert league.country == "Spain"
        assert league.available_seasons == "2023-24, 2024-25"
        assert league.gender is None
        assert league.tier is None

    def test_creates_with_all_fields(self) -> None:
        """Test creating LeagueSummary with all fields."""
        league = LeagueSummary(
            id=1,
            name="La Liga",
            country="Spain",
            gender="M",
            tier="1",
            available_seasons="2023-24, 2024-25",
        )
        assert league.gender == "M"
        assert league.tier == "1"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSummary(name="La Liga", country="Spain", available_seasons="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSummary(id=1, country="Spain", available_seasons="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_country(self) -> None:
        """Test that country is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSummary(id=1, name="La Liga", available_seasons="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country",) for error in errors)

    def test_requires_available_seasons(self) -> None:
        """Test that available_seasons is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSummary(id=1, name="La Liga", country="Spain")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("available_seasons",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSummary(id="not_int", name="La Liga", country="Spain", available_seasons="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            LeagueSummary(id=1, name=123, country="Spain", available_seasons="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that league names with unicode characters work."""
        league = LeagueSummary(
            id=1,
            name="Ligue 1",
            country="France",
            available_seasons="2023-24",
        )
        assert league.name == "Ligue 1"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        league = LeagueSummary(
            id=1,
            name="La Liga",
            country="Spain",
            gender="M",
            tier="1",
            available_seasons="2023-24",
        )
        data = league.model_dump()
        assert data["id"] == 1
        assert data["name"] == "La Liga"
        assert data["country"] == "Spain"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": 1,
            "name": "La Liga",
            "country": "Spain",
            "gender": "M",
            "tier": "1",
            "available_seasons": "2023-24",
        }
        league = LeagueSummary.model_validate(data)
        assert league.id == 1
        assert league.name == "La Liga"
        assert league.country == "Spain"


class TestLeaguesListResponse:
    """Test LeaguesListResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating LeaguesListResponse with empty list."""
        response = LeaguesListResponse(leagues=[])
        assert response.leagues == []

    def test_creates_with_leagues(self) -> None:
        """Test creating LeaguesListResponse with leagues."""
        league1 = LeagueSummary(
            id=1,
            name="La Liga",
            country="Spain",
            gender=None,
            tier=None,
            available_seasons="2023-24",
        )
        league2 = LeagueSummary(
            id=2,
            name="Premier League",
            country="England",
            gender=None,
            tier=None,
            available_seasons="2023-24",
        )
        response = LeaguesListResponse(leagues=[league1, league2])
        assert len(response.leagues) == 2
        assert response.leagues[0].name == "La Liga"
        assert response.leagues[1].name == "Premier League"

    def test_requires_leagues(self) -> None:
        """Test that leagues is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeaguesListResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("leagues",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that leagues must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            LeaguesListResponse(leagues="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("leagues",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        league = LeagueSummary(
            id=1,
            name="La Liga",
            country="Spain",
            available_seasons="2023-24",
        )
        response = LeaguesListResponse(leagues=[league])
        data = response.model_dump()
        assert len(data["leagues"]) == 1
        assert data["leagues"][0]["name"] == "La Liga"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "leagues": [
                {
                    "id": 1,
                    "name": "La Liga",
                    "country": "Spain",
                    "gender": None,
                    "tier": None,
                    "available_seasons": "2023-24",
                }
            ]
        }
        response = LeaguesListResponse.model_validate(data)
        assert len(response.leagues) == 1
        assert response.leagues[0].name == "La Liga"


class TestLeagueSeasonsResponse:
    """Test LeagueSeasonsResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating LeagueSeasonsResponse with empty list."""
        response = LeagueSeasonsResponse(seasons=[])
        assert response.seasons == []

    def test_creates_with_seasons(self, sample_season_display: SeasonDisplay) -> None:
        """Test creating LeagueSeasonsResponse with seasons."""
        season2 = SeasonDisplay(id=2, start_year=2024, end_year=None, display_name="2024-25")
        response = LeagueSeasonsResponse(seasons=[sample_season_display, season2])
        assert len(response.seasons) == 2
        assert response.seasons[0].display_name == "2023-24"
        assert response.seasons[1].display_name == "2024-25"

    def test_requires_seasons(self) -> None:
        """Test that seasons is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSeasonsResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("seasons",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that seasons must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueSeasonsResponse(seasons="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("seasons",) for error in errors)

    def test_serializes_to_dict(self, sample_season_display: SeasonDisplay) -> None:
        """Test serialization to dictionary."""
        response = LeagueSeasonsResponse(seasons=[sample_season_display])
        data = response.model_dump()
        assert len(data["seasons"]) == 1
        assert data["seasons"][0]["display_name"] == "2023-24"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "seasons": [
                {"id": 1, "start_year": 2023, "end_year": None, "display_name": "2023-24"}
            ]
        }
        response = LeagueSeasonsResponse.model_validate(data)
        assert len(response.seasons) == 1
        assert response.seasons[0].display_name == "2023-24"


class TestLeagueInfo:
    """Test LeagueInfo schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating LeagueInfo with required fields."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        assert league.id == 1
        assert league.name == "La Liga"
        assert league.country == "Spain"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueInfo(name="La Liga", country="Spain")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueInfo(id=1, country="Spain")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_country(self) -> None:
        """Test that country is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueInfo(id=1, name="La Liga")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueInfo(id="not_int", name="La Liga", country="Spain")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            LeagueInfo(id=1, name=123, country="Spain")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that league names with unicode characters work."""
        league = LeagueInfo(id=1, name="Ligue 1", country="France")
        assert league.name == "Ligue 1"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        data = league.model_dump()
        assert data["id"] == 1
        assert data["name"] == "La Liga"
        assert data["country"] == "Spain"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "La Liga", "country": "Spain"}
        league = LeagueInfo.model_validate(data)
        assert league.id == 1
        assert league.name == "La Liga"
        assert league.country == "Spain"


class TestLeagueTableEntry:
    """Test LeagueTableEntry schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating LeagueTableEntry with required fields."""
        entry = LeagueTableEntry(
            position=None,
            team_id=1,
            team_name="Barcelona",
            matches_played=None,
            wins=None,
            draws=None,
            losses=None,
            goals_for=None,
            goals_against=None,
            goal_difference=None,
            points=None,
        )
        assert entry.team_id == 1
        assert entry.team_name == "Barcelona"
        assert entry.position is None
        assert entry.matches_played is None

    def test_creates_with_all_fields(self) -> None:
        """Test creating LeagueTableEntry with all fields."""
        entry = LeagueTableEntry(
            position=1,
            team_id=1,
            team_name="Barcelona",
            matches_played=10,
            wins=8,
            draws=1,
            losses=1,
            goals_for=25,
            goals_against=10,
            goal_difference=15,
            points=25,
        )
        assert entry.position == 1
        assert entry.matches_played == 10
        assert entry.wins == 8
        assert entry.points == 25

    def test_accepts_zero_values(self) -> None:
        """Test that zero is a valid value for numeric fields."""
        entry = LeagueTableEntry(
            position=0,
            team_id=1,
            team_name="Barcelona",
            matches_played=0,
            wins=0,
            draws=0,
            losses=0,
            goals_for=0,
            goals_against=0,
            goal_difference=0,
            points=0,
        )
        assert entry.matches_played == 0
        assert entry.wins == 0
        assert entry.points == 0

    def test_requires_team_id(self) -> None:
        """Test that team_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableEntry(team_name="Barcelona")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team_id",) for error in errors)

    def test_requires_team_name(self) -> None:
        """Test that team_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableEntry(team_id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team_name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableEntry(team_id="not_int", team_name="Barcelona")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team_id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            LeagueTableEntry(team_id=1, team_name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team_name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that team names with unicode characters work."""
        entry = LeagueTableEntry(team_id=1, team_name="São Paulo")
        assert entry.team_name == "São Paulo"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        entry = LeagueTableEntry(
            position=1,
            team_id=1,
            team_name="Barcelona",
            matches_played=10,
            points=25,
        )
        data = entry.model_dump()
        assert data["position"] == 1
        assert data["team_id"] == 1
        assert data["team_name"] == "Barcelona"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "position": 1,
            "team_id": 1,
            "team_name": "Barcelona",
            "matches_played": 10,
            "wins": 8,
            "points": 25,
        }
        entry = LeagueTableEntry.model_validate(data)
        assert entry.position == 1
        assert entry.team_id == 1
        assert entry.team_name == "Barcelona"


class TestLeagueTableResponse:
    """Test LeagueTableResponse schema validation."""

    def test_creates_with_required_fields(
        self, sample_season_display: SeasonDisplay
    ) -> None:
        """Test creating LeagueTableResponse with required fields."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        entry = LeagueTableEntry(
            position=None,
            team_id=1,
            team_name="Barcelona",
            matches_played=None,
            wins=None,
            draws=None,
            losses=None,
            goals_for=None,
            goals_against=None,
            goal_difference=None,
            points=None,
        )

        response = LeagueTableResponse(league=league, season=sample_season_display, table=[entry])
        assert response.league.name == "La Liga"
        assert response.season.display_name == "2023-24"
        assert len(response.table) == 1

    def test_creates_with_empty_table(
        self, sample_season_display: SeasonDisplay
    ) -> None:
        """Test creating LeagueTableResponse with empty table."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        response = LeagueTableResponse(league=league, season=sample_season_display, table=[])
        assert response.table == []

    def test_requires_league(self, sample_season_display: SeasonDisplay) -> None:
        """Test that league is required."""
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableResponse(season=sample_season_display, table=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("league",) for error in errors)

    def test_requires_season(self) -> None:
        """Test that season is required."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableResponse(league=league, table=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season",) for error in errors)

    def test_requires_table(self, sample_season_display: SeasonDisplay) -> None:
        """Test that table is required."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableResponse(league=league, season=sample_season_display)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("table",) for error in errors)

    def test_validates_list_type(self, sample_season_display: SeasonDisplay) -> None:
        """Test that table must be a list."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        with pytest.raises(ValidationError) as exc_info:
            LeagueTableResponse(league=league, season=sample_season_display, table="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("table",) for error in errors)

    def test_serializes_to_dict(self, sample_season_display: SeasonDisplay) -> None:
        """Test serialization to dictionary."""
        league = LeagueInfo(id=1, name="La Liga", country="Spain")
        entry = LeagueTableEntry(team_id=1, team_name="Barcelona")
        response = LeagueTableResponse(league=league, season=sample_season_display, table=[entry])
        data = response.model_dump()
        assert data["league"]["name"] == "La Liga"
        assert data["season"]["display_name"] == "2023-24"
        assert len(data["table"]) == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "league": {"id": 1, "name": "La Liga", "country": "Spain"},
            "season": {"id": 1, "start_year": 2023, "end_year": None, "display_name": "2023-24"},
            "table": [{"team_id": 1, "team_name": "Barcelona"}],
        }
        response = LeagueTableResponse.model_validate(data)
        assert response.league.name == "La Liga"
        assert response.season.display_name == "2023-24"
        assert len(response.table) == 1
