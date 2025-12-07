"""Unit tests for clubs schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.clubs import (
    ClubByNation,
    ClubDetailsResponse,
    ClubInfo,
    ClubSummary,
    ClubsByNationResponse,
    CompetitionDisplay,
    CompetitionInfo,
    GoalLogEntry,
    NationBasic,
    NationDetailed,
    PlayerBasic,
    PlayerGoalLogEntry,
    PlayerGoalLogResponse,
    SquadPlayer,
    SeasonStats,
    TeamSeasonGoalLogResponse,
    TeamSeasonSquadResponse,
    TeamStatsInfo,
)
from app.schemas.players import PlayerStats, SeasonDisplay


class TestNationBasic:
    """Test NationBasic schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating NationBasic with required fields."""
        nation = NationBasic(id=1, name="Argentina", country_code="AR")
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationBasic(name="Argentina", country_code="AR")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationBasic(id=1, country_code="AR")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_country_code(self) -> None:
        """Test that country_code is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationBasic(id=1, name="Argentina")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country_code",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            NationBasic(id="not_int", name="Argentina", country_code="AR")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationBasic(id=1, name=123, country_code="AR")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that nation names with unicode characters work."""
        nation = NationBasic(id=1, name="Côte d'Ivoire", country_code="CI")
        assert nation.name == "Côte d'Ivoire"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationBasic(id=1, name="Argentina", country_code="AR")
        data = nation.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Argentina"
        assert data["country_code"] == "AR"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Argentina", "country_code": "AR"}
        nation = NationBasic.model_validate(data)
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"


class TestClubSummary:
    """Test ClubSummary schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating ClubSummary with required fields."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        assert club.id == 1
        assert club.name == "Barcelona"
        assert club.avg_position == 2.5

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubSummary(name="Barcelona", avg_position=2.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubSummary(id=1, avg_position=2.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_avg_position(self) -> None:
        """Test that avg_position is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubSummary(id=1, name="Barcelona")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("avg_position",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            ClubSummary(id="not_int", name="Barcelona", avg_position=2.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            ClubSummary(id=1, name=123, avg_position=2.5)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            ClubSummary(id=1, name="Barcelona", avg_position="not_float")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("avg_position",) for error in errors)

    def test_accepts_zero_avg_position(self) -> None:
        """Test that zero is a valid value for avg_position."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=0.0)
        assert club.avg_position == 0.0

    def test_accepts_unicode_in_names(self) -> None:
        """Test that club names with unicode characters work."""
        club = ClubSummary(id=1, name="São Paulo", avg_position=5.0)
        assert club.name == "São Paulo"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        data = club.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Barcelona"
        assert data["avg_position"] == 2.5

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Barcelona", "avg_position": 2.5}
        club = ClubSummary.model_validate(data)
        assert club.id == 1
        assert club.name == "Barcelona"
        assert club.avg_position == 2.5


class TestClubByNation:
    """Test ClubByNation schema validation."""

    def test_creates_with_required_fields(self, sample_nation_basic: NationBasic) -> None:
        """Test creating ClubByNation with required fields."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        club_by_nation = ClubByNation(nation=sample_nation_basic, clubs=[club])
        assert club_by_nation.nation.id == 1
        assert len(club_by_nation.clubs) == 1
        assert club_by_nation.clubs[0].name == "Barcelona"

    def test_creates_with_empty_clubs_list(self, sample_nation_basic: NationBasic) -> None:
        """Test creating ClubByNation with empty clubs list."""
        club_by_nation = ClubByNation(nation=sample_nation_basic, clubs=[])
        assert club_by_nation.clubs == []

    def test_requires_nation(self) -> None:
        """Test that nation is required."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        with pytest.raises(ValidationError) as exc_info:
            ClubByNation(clubs=[club])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nation",) for error in errors)

    def test_requires_clubs(self, sample_nation_basic: NationBasic) -> None:
        """Test that clubs is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubByNation(nation=sample_nation_basic)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("clubs",) for error in errors)

    def test_validates_list_type(self, sample_nation_basic: NationBasic) -> None:
        """Test that clubs must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            ClubByNation(nation=sample_nation_basic, clubs="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("clubs",) for error in errors)

    def test_serializes_to_dict(self, sample_nation_basic: NationBasic) -> None:
        """Test serialization to dictionary."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        club_by_nation = ClubByNation(nation=sample_nation_basic, clubs=[club])
        data = club_by_nation.model_dump()
        assert data["nation"]["id"] == 1
        assert len(data["clubs"]) == 1
        assert data["clubs"][0]["name"] == "Barcelona"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            "clubs": [{"id": 1, "name": "Barcelona", "avg_position": 2.5}],
        }
        club_by_nation = ClubByNation.model_validate(data)
        assert club_by_nation.nation.id == 1
        assert len(club_by_nation.clubs) == 1


class TestClubsByNationResponse:
    """Test ClubsByNationResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating ClubsByNationResponse with empty list."""
        response = ClubsByNationResponse(nations=[])
        assert response.nations == []

    def test_creates_with_nations(self, sample_nation_basic: NationBasic) -> None:
        """Test creating ClubsByNationResponse with nations."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        club_by_nation = ClubByNation(nation=sample_nation_basic, clubs=[club])
        response = ClubsByNationResponse(nations=[club_by_nation])
        assert len(response.nations) == 1

    def test_requires_nations(self) -> None:
        """Test that nations is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubsByNationResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nations",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that nations must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            ClubsByNationResponse(nations="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nations",) for error in errors)

    def test_serializes_to_dict(self, sample_nation_basic: NationBasic) -> None:
        """Test serialization to dictionary."""
        club = ClubSummary(id=1, name="Barcelona", avg_position=2.5)
        club_by_nation = ClubByNation(nation=sample_nation_basic, clubs=[club])
        response = ClubsByNationResponse(nations=[club_by_nation])
        data = response.model_dump()
        assert len(data["nations"]) == 1
        assert data["nations"][0]["nation"]["id"] == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "nations": [
                {
                    "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
                    "clubs": [{"id": 1, "name": "Barcelona", "avg_position": 2.5}],
                }
            ]
        }
        response = ClubsByNationResponse.model_validate(data)
        assert len(response.nations) == 1


class TestNationDetailed:
    """Test NationDetailed schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating NationDetailed with required fields."""
        nation = NationDetailed(id=1, name="Argentina", country_code=None)
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code is None

    def test_creates_with_all_fields(self) -> None:
        """Test creating NationDetailed with all fields."""
        nation = NationDetailed(id=1, name="Argentina", country_code="AR")
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetailed(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_none_for_id(self) -> None:
        """Test that id can be None."""
        nation = NationDetailed(id=None, name="Argentina", country_code=None)
        assert nation.id is None
        assert nation.name == "Argentina"

    def test_accepts_none_for_country_code(self) -> None:
        """Test that country_code can be None."""
        nation = NationDetailed(id=1, name="Argentina", country_code=None)
        assert nation.country_code is None

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            NationDetailed(id="not_int", name="Argentina")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            NationDetailed(id=1, name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that nation names with unicode characters work."""
        nation = NationDetailed(id=1, name="Côte d'Ivoire", country_code="CI")
        assert nation.name == "Côte d'Ivoire"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationDetailed(id=1, name="Argentina", country_code="AR")
        data = nation.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Argentina"
        assert data["country_code"] == "AR"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Argentina", "country_code": "AR"}
        nation = NationDetailed.model_validate(data)
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"


class TestClubInfo:
    """Test ClubInfo schema validation."""

    def test_creates_with_required_fields(self, sample_nation_detailed: NationDetailed) -> None:
        """Test creating ClubInfo with required fields."""
        club = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        assert club.id == 1
        assert club.name == "Barcelona"
        assert club.nation.name == "Argentina"

    def test_requires_id(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubInfo(name="Barcelona", nation=sample_nation_detailed)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubInfo(id=1, nation=sample_nation_detailed)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_nation(self) -> None:
        """Test that nation is required."""
        with pytest.raises(ValidationError) as exc_info:
            ClubInfo(id=1, name="Barcelona")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("nation",) for error in errors)

    def test_accepts_unicode_in_names(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that club names with unicode characters work."""
        club = ClubInfo(id=1, name="São Paulo", nation=sample_nation_detailed)
        assert club.name == "São Paulo"

    def test_serializes_to_dict(self, sample_nation_detailed: NationDetailed) -> None:
        """Test serialization to dictionary."""
        club = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        data = club.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Barcelona"
        assert data["nation"]["name"] == "Argentina"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": 1,
            "name": "Barcelona",
            "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
        }
        club = ClubInfo.model_validate(data)
        assert club.id == 1
        assert club.name == "Barcelona"
        assert club.nation.name == "Argentina"


class TestCompetitionInfo:
    """Test CompetitionInfo schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating CompetitionInfo with required fields."""
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        assert competition.id == 1
        assert competition.name == "La Liga"
        assert competition.tier is None

    def test_creates_with_tier(self) -> None:
        """Test creating CompetitionInfo with tier."""
        competition = CompetitionInfo(id=1, name="La Liga", tier="1")
        assert competition.tier == "1"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionInfo(name="La Liga")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionInfo(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionInfo(id="not_int", name="La Liga")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CompetitionInfo(id=1, name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        competition = CompetitionInfo(id=1, name="La Liga", tier="1")
        data = competition.model_dump()
        assert data["id"] == 1
        assert data["name"] == "La Liga"
        assert data["tier"] == "1"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "La Liga", "tier": "1"}
        competition = CompetitionInfo.model_validate(data)
        assert competition.id == 1
        assert competition.name == "La Liga"
        assert competition.tier == "1"


class TestTeamStatsInfo:
    """Test TeamStatsInfo schema validation."""

    def test_all_fields_optional(self, empty_team_stats_info: TeamStatsInfo) -> None:
        """Test that all fields are optional."""
        assert empty_team_stats_info.ranking is None
        assert empty_team_stats_info.matches_played is None
        assert empty_team_stats_info.wins is None

    def test_creates_with_all_fields(self) -> None:
        """Test creating TeamStatsInfo with all fields."""
        stats = TeamStatsInfo(
            ranking=1,
            matches_played=10,
            wins=8,
            draws=1,
            losses=1,
            goals_for=25,
            goals_against=10,
            goal_difference=15,
            points=25,
            attendance=50000,
            notes="Champions",
        )
        assert stats.ranking == 1
        assert stats.matches_played == 10
        assert stats.wins == 8
        assert stats.points == 25
        assert stats.notes == "Champions"

    def test_accepts_zero_values(self) -> None:
        """Test that zero is a valid value for numeric fields."""
        stats = TeamStatsInfo(
            ranking=0,
            matches_played=0,
            wins=0,
            draws=0,
            losses=0,
            goals_for=0,
            goals_against=0,
            goal_difference=0,
            points=0,
            attendance=0,
        )
        assert stats.matches_played == 0
        assert stats.wins == 0
        assert stats.points == 0

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            TeamStatsInfo(ranking="not_int")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("ranking",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            TeamStatsInfo(matches_played="not_int")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("matches_played",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            TeamStatsInfo(notes=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("notes",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        stats = TeamStatsInfo(ranking=1, matches_played=10, wins=8, points=25)
        data = stats.model_dump()
        assert data["ranking"] == 1
        assert data["matches_played"] == 10
        assert data["points"] == 25

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "ranking": 1,
            "matches_played": 10,
            "wins": 8,
            "points": 25,
        }
        stats = TeamStatsInfo.model_validate(data)
        assert stats.ranking == 1
        assert stats.matches_played == 10
        assert stats.points == 25


class TestSeasonStats:
    """Test SeasonStats schema validation."""

    def test_creates_with_required_fields(
        self,
        sample_season_display: SeasonDisplay,
        empty_team_stats_info: TeamStatsInfo,
    ) -> None:
        """Test creating SeasonStats with required fields."""
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        season_stats = SeasonStats(
            season=sample_season_display,
            competition=competition,
            stats=empty_team_stats_info,
        )
        assert season_stats.season.id == 1
        assert season_stats.competition.id == 1
        assert season_stats.stats is not None

    def test_requires_season(self, empty_team_stats_info: TeamStatsInfo) -> None:
        """Test that season is required."""
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        with pytest.raises(ValidationError) as exc_info:
            SeasonStats(competition=competition, stats=empty_team_stats_info)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season",) for error in errors)

    def test_requires_competition(
        self,
        sample_season_display: SeasonDisplay,
        empty_team_stats_info: TeamStatsInfo,
    ) -> None:
        """Test that competition is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonStats(season=sample_season_display, stats=empty_team_stats_info)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("competition",) for error in errors)

    def test_requires_stats(
        self,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test that stats is required."""
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        with pytest.raises(ValidationError) as exc_info:
            SeasonStats(season=sample_season_display, competition=competition)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("stats",) for error in errors)

    def test_serializes_to_dict(
        self,
        sample_season_display: SeasonDisplay,
        empty_team_stats_info: TeamStatsInfo,
    ) -> None:
        """Test serialization to dictionary."""
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        season_stats = SeasonStats(
            season=sample_season_display,
            competition=competition,
            stats=empty_team_stats_info,
        )
        data = season_stats.model_dump()
        assert data["season"]["id"] == 1
        assert data["competition"]["id"] == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "season": {"id": 1, "start_year": 2023, "end_year": None, "display_name": "2023-24"},
            "competition": {"id": 1, "name": "La Liga", "tier": None},
            "stats": {},
        }
        season_stats = SeasonStats.model_validate(data)
        assert season_stats.season.id == 1
        assert season_stats.competition.id == 1


class TestClubDetailsResponse:
    """Test ClubDetailsResponse schema validation."""

    def test_creates_with_required_fields(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
        empty_team_stats_info: TeamStatsInfo,
    ) -> None:
        """Test creating ClubDetailsResponse with required fields."""
        club = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        season_stats = SeasonStats(
            season=sample_season_display,
            competition=competition,
            stats=empty_team_stats_info,
        )

        response = ClubDetailsResponse(club=club, seasons=[season_stats])
        assert response.club.name == "Barcelona"
        assert len(response.seasons) == 1

    def test_creates_with_empty_seasons_list(
        self, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test creating ClubDetailsResponse with empty seasons list."""
        club = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        response = ClubDetailsResponse(club=club, seasons=[])
        assert response.seasons == []

    def test_requires_club(
        self,
        sample_season_display: SeasonDisplay,
        empty_team_stats_info: TeamStatsInfo,
    ) -> None:
        """Test that club is required."""
        competition = CompetitionInfo(id=1, name="La Liga", tier=None)
        season_stats = SeasonStats(
            season=sample_season_display,
            competition=competition,
            stats=empty_team_stats_info,
        )
        with pytest.raises(ValidationError) as exc_info:
            ClubDetailsResponse(seasons=[season_stats])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("club",) for error in errors)

    def test_requires_seasons(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that seasons is required."""
        club = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            ClubDetailsResponse(club=club)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("seasons",) for error in errors)

    def test_serializes_to_dict(self, sample_nation_detailed: NationDetailed) -> None:
        """Test serialization to dictionary."""
        club = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        response = ClubDetailsResponse(club=club, seasons=[])
        data = response.model_dump()
        assert data["club"]["name"] == "Barcelona"
        assert data["seasons"] == []

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "club": {
                "id": 1,
                "name": "Barcelona",
                "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            },
            "seasons": [],
        }
        response = ClubDetailsResponse.model_validate(data)
        assert response.club.name == "Barcelona"
        assert response.seasons == []


class TestPlayerBasic:
    """Test PlayerBasic schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating PlayerBasic with required fields."""
        player = PlayerBasic(id=1, name="Lionel Messi")
        assert player.id == 1
        assert player.name == "Lionel Messi"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerBasic(name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerBasic(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerBasic(id="not_int", name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            PlayerBasic(id=1, name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that player names with unicode characters work."""
        player = PlayerBasic(id=1, name="José Mourinho")
        assert player.name == "José Mourinho"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = PlayerBasic(id=1, name="Lionel Messi")
        data = player.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Lionel Messi"}
        player = PlayerBasic.model_validate(data)
        assert player.id == 1
        assert player.name == "Lionel Messi"


class TestSquadPlayer:
    """Test SquadPlayer schema validation."""

    def test_creates_with_required_fields(
        self, sample_player_basic: PlayerBasic, empty_player_stats: PlayerStats
    ) -> None:
        """Test creating SquadPlayer with required fields."""
        stats = PlayerStats(goals_scored=10)
        squad_player = SquadPlayer(player=sample_player_basic, stats=stats)
        assert squad_player.player.name == "Lionel Messi"
        assert squad_player.stats.goals_scored == 10

    def test_requires_player(self, empty_player_stats: PlayerStats) -> None:
        """Test that player is required."""
        with pytest.raises(ValidationError) as exc_info:
            SquadPlayer(stats=empty_player_stats)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player",) for error in errors)

    def test_requires_stats(self, sample_player_basic: PlayerBasic) -> None:
        """Test that stats is required."""
        with pytest.raises(ValidationError) as exc_info:
            SquadPlayer(player=sample_player_basic)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("stats",) for error in errors)

    def test_serializes_to_dict(
        self, sample_player_basic: PlayerBasic, empty_player_stats: PlayerStats
    ) -> None:
        """Test serialization to dictionary."""
        squad_player = SquadPlayer(player=sample_player_basic, stats=empty_player_stats)
        data = squad_player.model_dump()
        assert data["player"]["name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "player": {"id": 1, "name": "Lionel Messi"},
            "stats": {},
        }
        squad_player = SquadPlayer.model_validate(data)
        assert squad_player.player.name == "Lionel Messi"


class TestCompetitionDisplay:
    """Test CompetitionDisplay schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating CompetitionDisplay with required fields."""
        competition = CompetitionDisplay(id=1, name="La Liga")
        assert competition.id == 1
        assert competition.name == "La Liga"

    def test_creates_with_none_id(self) -> None:
        """Test creating CompetitionDisplay with None id."""
        competition = CompetitionDisplay(id=None, name="La Liga")
        assert competition.id is None
        assert competition.name == "La Liga"

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionDisplay(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            CompetitionDisplay(id="not_int", name="La Liga")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            CompetitionDisplay(id=1, name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        competition = CompetitionDisplay(id=1, name="La Liga")
        data = competition.model_dump()
        assert data["id"] == 1
        assert data["name"] == "La Liga"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "La Liga"}
        competition = CompetitionDisplay.model_validate(data)
        assert competition.id == 1
        assert competition.name == "La Liga"


class TestTeamSeasonSquadResponse:
    """Test TeamSeasonSquadResponse schema validation."""

    def test_creates_with_required_fields(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
        sample_player_basic: PlayerBasic,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test creating TeamSeasonSquadResponse with required fields."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        squad_player = SquadPlayer(player=sample_player_basic, stats=empty_player_stats)

        response = TeamSeasonSquadResponse(
            team=team,
            season=sample_season_display,
            competition=competition,
            players=[squad_player],
        )
        assert response.team.name == "Barcelona"
        assert response.season.display_name == "2023-24"
        assert len(response.players) == 1

    def test_creates_with_empty_players_list(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test creating TeamSeasonSquadResponse with empty players list."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        response = TeamSeasonSquadResponse(
            team=team, season=sample_season_display, competition=competition, players=[]
        )
        assert response.players == []

    def test_requires_team(self, sample_season_display: SeasonDisplay) -> None:
        """Test that team is required."""
        competition = CompetitionDisplay(id=1, name="La Liga")
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonSquadResponse(season=sample_season_display, competition=competition, players=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team",) for error in errors)

    def test_requires_season(
        self, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test that season is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonSquadResponse(team=team, competition=competition, players=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season",) for error in errors)

    def test_requires_competition(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test that competition is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonSquadResponse(team=team, season=sample_season_display, players=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("competition",) for error in errors)

    def test_requires_players(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test that players is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonSquadResponse(team=team, season=sample_season_display, competition=competition)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("players",) for error in errors)

    def test_serializes_to_dict(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
        sample_player_basic: PlayerBasic,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test serialization to dictionary."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        squad_player = SquadPlayer(player=sample_player_basic, stats=empty_player_stats)
        response = TeamSeasonSquadResponse(
            team=team,
            season=sample_season_display,
            competition=competition,
            players=[squad_player],
        )
        data = response.model_dump()
        assert data["team"]["name"] == "Barcelona"
        assert data["season"]["display_name"] == "2023-24"
        assert len(data["players"]) == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "team": {
                "id": 1,
                "name": "Barcelona",
                "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            },
            "season": {"id": 1, "start_year": 2023, "end_year": None, "display_name": "2023-24"},
            "competition": {"id": 1, "name": "La Liga"},
            "players": [{"player": {"id": 1, "name": "Lionel Messi"}, "stats": {}}],
        }
        response = TeamSeasonSquadResponse.model_validate(data)
        assert response.team.name == "Barcelona"
        assert response.season.display_name == "2023-24"
        assert len(response.players) == 1


class TestGoalLogEntry:
    """Test GoalLogEntry schema validation."""

    def test_creates_with_required_fields(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test creating GoalLogEntry with required fields."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            goal_value=None,
            xg=None,
            post_shot_xg=None,
            assisted_by=None,
        )
        assert goal.date == "2024-01-15"
        assert goal.scorer.name == "Lionel Messi"
        assert goal.minute == 45
        assert goal.goal_value is None
        assert goal.xg is None
        assert goal.assisted_by is None

    def test_creates_with_all_fields(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test creating GoalLogEntry with all fields."""
        assist = PlayerBasic(id=2, name="Xavi")
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            goal_value=2.5,
            xg=0.8,
            post_shot_xg=0.9,
            assisted_by=assist,
        )
        assert goal.goal_value == 2.5
        assert goal.xg == 0.8
        assert goal.assisted_by is not None
        assert goal.assisted_by.name == "Xavi"

    def test_requires_date(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test that date is required."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            GoalLogEntry(
                venue="Home",
                scorer=sample_player_basic,
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("date",) for error in errors)

    def test_requires_scorer(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that scorer is required."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            GoalLogEntry(
                date="2024-01-15",
                venue="Home",
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("scorer",) for error in errors)

    def test_requires_minute(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test that minute is required."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            GoalLogEntry(
                date="2024-01-15",
                venue="Home",
                scorer=sample_player_basic,
                opponent=opponent,
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("minute",) for error in errors)

    def test_validates_types(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test that types are validated."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            GoalLogEntry(
                date="2024-01-15",
                venue="Home",
                scorer=sample_player_basic,
                opponent=opponent,
                minute="not_int",
                score_before="1-0",
                score_after="2-0",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("minute",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            GoalLogEntry(
                date="2024-01-15",
                venue="Home",
                scorer=sample_player_basic,
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
                goal_value="not_float",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goal_value",) for error in errors)

    def test_accepts_zero_minute(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test that zero is a valid value for minute."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=0,
            score_before="0-0",
            score_after="1-0",
        )
        assert goal.minute == 0

    def test_accepts_zero_goal_value(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test that zero is a valid value for goal_value."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            goal_value=0.0,
        )
        assert goal.goal_value == 0.0

    def test_serializes_to_dict(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test serialization to dictionary."""
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            goal_value=2.5,
        )
        data = goal.model_dump()
        assert data["date"] == "2024-01-15"
        assert data["minute"] == 45
        assert data["goal_value"] == 2.5

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "date": "2024-01-15",
            "venue": "Home",
            "scorer": {"id": 1, "name": "Lionel Messi"},
            "opponent": {
                "id": 2,
                "name": "Real Madrid",
                "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            },
            "minute": 45,
            "score_before": "1-0",
            "score_after": "2-0",
            "goal_value": 2.5,
        }
        goal = GoalLogEntry.model_validate(data)
        assert goal.date == "2024-01-15"
        assert goal.minute == 45
        assert goal.goal_value == 2.5


class TestTeamSeasonGoalLogResponse:
    """Test TeamSeasonGoalLogResponse schema validation."""

    def test_creates_with_required_fields(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
        sample_player_basic: PlayerBasic,
    ) -> None:
        """Test creating TeamSeasonGoalLogResponse with required fields."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
        )

        response = TeamSeasonGoalLogResponse(
            team=team, season=sample_season_display, competition=competition, goals=[goal]
        )
        assert response.team.name == "Barcelona"
        assert response.season.display_name == "2023-24"
        assert len(response.goals) == 1

    def test_creates_with_empty_goals_list(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test creating TeamSeasonGoalLogResponse with empty goals list."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        response = TeamSeasonGoalLogResponse(
            team=team, season=sample_season_display, competition=competition, goals=[]
        )
        assert response.goals == []

    def test_requires_team(self, sample_season_display: SeasonDisplay) -> None:
        """Test that team is required."""
        competition = CompetitionDisplay(id=1, name="La Liga")
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonGoalLogResponse(season=sample_season_display, competition=competition, goals=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team",) for error in errors)

    def test_requires_season(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that season is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonGoalLogResponse(team=team, competition=competition, goals=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season",) for error in errors)

    def test_requires_competition(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test that competition is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonGoalLogResponse(team=team, season=sample_season_display, goals=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("competition",) for error in errors)

    def test_requires_goals(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
    ) -> None:
        """Test that goals is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        with pytest.raises(ValidationError) as exc_info:
            TeamSeasonGoalLogResponse(team=team, season=sample_season_display, competition=competition)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goals",) for error in errors)

    def test_serializes_to_dict(
        self,
        sample_nation_detailed: NationDetailed,
        sample_season_display: SeasonDisplay,
        sample_player_basic: PlayerBasic,
    ) -> None:
        """Test serialization to dictionary."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        competition = CompetitionDisplay(id=1, name="La Liga")
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = GoalLogEntry(
            date="2024-01-15",
            venue="Home",
            scorer=sample_player_basic,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
        )
        response = TeamSeasonGoalLogResponse(
            team=team, season=sample_season_display, competition=competition, goals=[goal]
        )
        data = response.model_dump()
        assert data["team"]["name"] == "Barcelona"
        assert data["season"]["display_name"] == "2023-24"
        assert len(data["goals"]) == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "team": {
                "id": 1,
                "name": "Barcelona",
                "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            },
            "season": {"id": 1, "start_year": 2023, "end_year": None, "display_name": "2023-24"},
            "competition": {"id": 1, "name": "La Liga"},
            "goals": [
                {
                    "date": "2024-01-15",
                    "venue": "Home",
                    "scorer": {"id": 1, "name": "Lionel Messi"},
                    "opponent": {
                        "id": 2,
                        "name": "Real Madrid",
                        "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
                    },
                    "minute": 45,
                    "score_before": "1-0",
                    "score_after": "2-0",
                }
            ],
        }
        response = TeamSeasonGoalLogResponse.model_validate(data)
        assert response.team.name == "Barcelona"
        assert response.season.display_name == "2023-24"
        assert len(response.goals) == 1


class TestPlayerGoalLogEntry:
    """Test PlayerGoalLogEntry schema validation."""

    def test_creates_with_required_fields(
        self, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test creating PlayerGoalLogEntry with required fields."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            season_id=1,
            season_display_name="2023-24",
            goal_value=None,
            xg=None,
            post_shot_xg=None,
            assisted_by=None,
        )
        assert goal.date == "2024-01-15"
        assert goal.team.name == "Barcelona"
        assert goal.minute == 45
        assert goal.season_id == 1
        assert goal.season_display_name == "2023-24"
        assert goal.goal_value is None
        assert goal.assisted_by is None

    def test_creates_with_all_fields(
        self, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test creating PlayerGoalLogEntry with all fields."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        assist = PlayerBasic(id=2, name="Xavi")
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            goal_value=2.5,
            xg=0.8,
            post_shot_xg=0.9,
            assisted_by=assist,
            season_id=1,
            season_display_name="2023-24",
        )
        assert goal.goal_value == 2.5
        assert goal.assisted_by is not None
        assert goal.assisted_by.name == "Xavi"

    def test_requires_date(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that date is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogEntry(
                venue="Home",
                team=team,
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
                season_id=1,
                season_display_name="2023-24",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("date",) for error in errors)

    def test_requires_season_id(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that season_id is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogEntry(
                date="2024-01-15",
                venue="Home",
                team=team,
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
                season_display_name="2023-24",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season_id",) for error in errors)

    def test_requires_season_display_name(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that season_display_name is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogEntry(
                date="2024-01-15",
                venue="Home",
                team=team,
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
                season_id=1,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season_display_name",) for error in errors)

    def test_validates_types(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that types are validated."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogEntry(
                date="2024-01-15",
                venue="Home",
                team=team,
                opponent=opponent,
                minute="not_int",
                score_before="1-0",
                score_after="2-0",
                season_id=1,
                season_display_name="2023-24",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("minute",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogEntry(
                date="2024-01-15",
                venue="Home",
                team=team,
                opponent=opponent,
                minute=45,
                score_before="1-0",
                score_after="2-0",
                season_id="not_int",
                season_display_name="2023-24",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season_id",) for error in errors)

    def test_accepts_zero_values(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that zero is a valid value for numeric fields."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=0,
            score_before="0-0",
            score_after="1-0",
            season_id=0,
            season_display_name="2023-24",
            goal_value=0.0,
        )
        assert goal.minute == 0
        assert goal.season_id == 0
        assert goal.goal_value == 0.0

    def test_serializes_to_dict(self, sample_nation_detailed: NationDetailed) -> None:
        """Test serialization to dictionary."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            season_id=1,
            season_display_name="2023-24",
            goal_value=2.5,
        )
        data = goal.model_dump()
        assert data["date"] == "2024-01-15"
        assert data["minute"] == 45
        assert data["season_id"] == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "date": "2024-01-15",
            "venue": "Home",
            "team": {
                "id": 1,
                "name": "Barcelona",
                "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            },
            "opponent": {
                "id": 2,
                "name": "Real Madrid",
                "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
            },
            "minute": 45,
            "score_before": "1-0",
            "score_after": "2-0",
            "season_id": 1,
            "season_display_name": "2023-24",
            "goal_value": 2.5,
        }
        goal = PlayerGoalLogEntry.model_validate(data)
        assert goal.date == "2024-01-15"
        assert goal.minute == 45
        assert goal.season_id == 1


class TestPlayerGoalLogResponse:
    """Test PlayerGoalLogResponse schema validation."""

    def test_creates_with_required_fields(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test creating PlayerGoalLogResponse with required fields."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            season_id=1,
            season_display_name="2023-24",
        )

        response = PlayerGoalLogResponse(player=sample_player_basic, goals=[goal])
        assert response.player.name == "Lionel Messi"
        assert len(response.goals) == 1

    def test_creates_with_empty_goals_list(self, sample_player_basic: PlayerBasic) -> None:
        """Test creating PlayerGoalLogResponse with empty goals list."""
        response = PlayerGoalLogResponse(player=sample_player_basic, goals=[])
        assert response.goals == []

    def test_requires_player(self, sample_nation_detailed: NationDetailed) -> None:
        """Test that player is required."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            season_id=1,
            season_display_name="2023-24",
        )
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogResponse(goals=[goal])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player",) for error in errors)

    def test_requires_goals(self, sample_player_basic: PlayerBasic) -> None:
        """Test that goals is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogResponse(player=sample_player_basic)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goals",) for error in errors)

    def test_validates_list_type(self, sample_player_basic: PlayerBasic) -> None:
        """Test that goals must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerGoalLogResponse(player=sample_player_basic, goals="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goals",) for error in errors)

    def test_serializes_to_dict(
        self, sample_player_basic: PlayerBasic, sample_nation_detailed: NationDetailed
    ) -> None:
        """Test serialization to dictionary."""
        team = ClubInfo(id=1, name="Barcelona", nation=sample_nation_detailed)
        opponent = ClubInfo(id=2, name="Real Madrid", nation=sample_nation_detailed)
        goal = PlayerGoalLogEntry(
            date="2024-01-15",
            venue="Home",
            team=team,
            opponent=opponent,
            minute=45,
            score_before="1-0",
            score_after="2-0",
            season_id=1,
            season_display_name="2023-24",
        )
        response = PlayerGoalLogResponse(player=sample_player_basic, goals=[goal])
        data = response.model_dump()
        assert data["player"]["name"] == "Lionel Messi"
        assert len(data["goals"]) == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "player": {"id": 1, "name": "Lionel Messi"},
            "goals": [
                {
                    "date": "2024-01-15",
                    "venue": "Home",
                    "team": {
                        "id": 1,
                        "name": "Barcelona",
                        "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
                    },
                    "opponent": {
                        "id": 2,
                        "name": "Real Madrid",
                        "nation": {"id": 1, "name": "Argentina", "country_code": "AR"},
                    },
                    "minute": 45,
                    "score_before": "1-0",
                    "score_after": "2-0",
                    "season_id": 1,
                    "season_display_name": "2023-24",
                }
            ],
        }
        response = PlayerGoalLogResponse.model_validate(data)
        assert response.player.name == "Lionel Messi"
        assert len(response.goals) == 1
