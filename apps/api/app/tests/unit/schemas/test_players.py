"""Unit tests for players schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.common import NationInfo
from app.schemas.players import (
    CareerTotals,
    CompetitionInfo,
    PlayerDetailsResponse,
    PlayerInfo,
    PlayerStats,
    SeasonData,
    SeasonDisplay,
    TeamInfo,
)


class TestPlayerInfo:
    """Test PlayerInfo schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating PlayerInfo with required fields."""
        player = PlayerInfo(id=1, name="Lionel Messi", nation=None)
        assert player.id == 1
        assert player.name == "Lionel Messi"
        assert player.nation is None

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerInfo(name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerInfo(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_nation(self, sample_nation_info: NationInfo) -> None:
        """Test that nation can be provided."""
        player = PlayerInfo(id=1, name="Lionel Messi", nation=sample_nation_info)
        assert player.nation is not None
        assert player.nation.id == 1
        assert player.nation.name == "Argentina"

    def test_accepts_none_nation(self) -> None:
        """Test that nation can be None."""
        player = PlayerInfo(id=1, name="Lionel Messi", nation=None)
        assert player.nation is None

    def test_validates_id_type(self) -> None:
        """Test that id must be an integer."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerInfo(id="not_an_int", name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_validates_name_type(self) -> None:
        """Test that name must be a string."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerInfo(id=1, name=12345)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that player names with unicode characters work."""
        player = PlayerInfo(id=1, name="José Mourinho", nation=None)
        assert player.name == "José Mourinho"

        player2 = PlayerInfo(id=2, name="N'Golo Kanté", nation=None)
        assert player2.name == "N'Golo Kanté"

        player3 = PlayerInfo(id=3, name="Müller", nation=None)
        assert player3.name == "Müller"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        player = PlayerInfo(id=1, name="Lionel Messi", nation=None)
        data = player.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Lionel Messi"
        assert data["nation"] is None

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Lionel Messi", "nation": None}
        player = PlayerInfo.model_validate(data)
        assert player.id == 1
        assert player.name == "Lionel Messi"
        assert player.nation is None


class TestSeasonDisplay:
    """Test SeasonDisplay schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating SeasonDisplay with required fields."""
        season = SeasonDisplay(id=1, start_year=2023, end_year=None, display_name="2023-24")
        assert season.id == 1
        assert season.start_year == 2023
        assert season.display_name == "2023-24"
        assert season.end_year is None

    def test_creates_with_all_fields(self) -> None:
        """Test creating SeasonDisplay with all fields."""
        season = SeasonDisplay(id=1, start_year=2023, end_year=2024, display_name="2023-24")
        assert season.id == 1
        assert season.start_year == 2023
        assert season.end_year == 2024
        assert season.display_name == "2023-24"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonDisplay(start_year=2023, display_name="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_start_year(self) -> None:
        """Test that start_year is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonDisplay(id=1, display_name="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("start_year",) for error in errors)

    def test_requires_display_name(self) -> None:
        """Test that display_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonDisplay(id=1, start_year=2023)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("display_name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonDisplay(id="not_int", start_year=2023, display_name="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            SeasonDisplay(id=1, start_year="not_int", display_name="2023-24")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("start_year",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            SeasonDisplay(id=1, start_year=2023, display_name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("display_name",) for error in errors)

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        season = SeasonDisplay(id=1, start_year=2023, end_year=2024, display_name="2023-24")
        data = season.model_dump()
        assert data["id"] == 1
        assert data["start_year"] == 2023
        assert data["end_year"] == 2024
        assert data["display_name"] == "2023-24"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "start_year": 2023, "end_year": 2024, "display_name": "2023-24"}
        season = SeasonDisplay.model_validate(data)
        assert season.id == 1
        assert season.start_year == 2023
        assert season.end_year == 2024
        assert season.display_name == "2023-24"


class TestTeamInfo:
    """Test TeamInfo schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating TeamInfo with required fields."""
        team = TeamInfo(id=1, name="Barcelona")
        assert team.id == 1
        assert team.name == "Barcelona"

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            TeamInfo(name="Barcelona")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            TeamInfo(id=1)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_types(self) -> None:
        """Test that types are validated."""
        with pytest.raises(ValidationError) as exc_info:
            TeamInfo(id="not_int", name="Barcelona")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            TeamInfo(id=1, name=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that team names with unicode characters work."""
        team = TeamInfo(id=1, name="São Paulo")
        assert team.name == "São Paulo"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        team = TeamInfo(id=1, name="Barcelona")
        data = team.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Barcelona"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Barcelona"}
        team = TeamInfo.model_validate(data)
        assert team.id == 1
        assert team.name == "Barcelona"


class TestCompetitionInfo:
    """Test CompetitionInfo schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating CompetitionInfo with required fields."""
        competition = CompetitionInfo(id=1, name="La Liga")
        assert competition.id == 1
        assert competition.name == "La Liga"

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
        competition = CompetitionInfo(id=1, name="La Liga")
        data = competition.model_dump()
        assert data["id"] == 1
        assert data["name"] == "La Liga"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "La Liga"}
        competition = CompetitionInfo.model_validate(data)
        assert competition.id == 1
        assert competition.name == "La Liga"


class TestPlayerStats:
    """Test PlayerStats schema validation."""

    def test_all_fields_optional(self, empty_player_stats: PlayerStats) -> None:
        """Test that all fields are optional."""
        assert empty_player_stats.matches_played is None
        assert empty_player_stats.goals_scored is None
        assert empty_player_stats.goal_value is None
        assert empty_player_stats.gv_avg is None

    def test_accepts_all_fields(self) -> None:
        """Test that all fields can be provided."""
        stats = PlayerStats(
            matches_played=10,
            matches_started=8,
            total_minutes=720,
            minutes_divided_90=8.0,
            goals_scored=5,
            assists=3,
            total_goal_assists=8,
            non_pk_goals=4,
            pk_made=1,
            pk_attempted=1,
            yellow_cards=2,
            red_cards=0,
            goal_value=12.5,
            gv_avg=1.25,
            goal_per_90=0.625,
            assists_per_90=0.375,
            total_goals_assists_per_90=1.0,
            non_pk_goals_per_90=0.5,
            non_pk_goal_and_assists_per_90=0.875,
        )
        assert stats.matches_played == 10
        assert stats.goals_scored == 5
        assert stats.goal_value == 12.5
        assert stats.gv_avg == 1.25

    def test_accepts_zero_values(self) -> None:
        """Test that zero is a valid value for numeric fields."""
        stats = PlayerStats(
            matches_played=0,
            matches_started=0,
            total_minutes=0,
            goals_scored=0,
            assists=0,
            yellow_cards=0,
            red_cards=0,
        )
        assert stats.matches_played == 0
        assert stats.goals_scored == 0
        assert stats.assists == 0

    def test_validates_int_types(self) -> None:
        """Test that integer fields validate types."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerStats(goals_scored="not_an_int")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goals_scored",) for error in errors)

    def test_validates_float_types(self) -> None:
        """Test that float fields validate types."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerStats(goal_value="not_a_float")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("goal_value",) for error in errors)

    def test_accepts_none_for_optional_fields(self, empty_player_stats: PlayerStats) -> None:
        """Test that None is accepted for optional fields."""
        assert empty_player_stats.matches_played is None
        assert empty_player_stats.goals_scored is None
        assert empty_player_stats.goal_value is None

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        stats = PlayerStats(goals_scored=10, assists=5, goal_value=12.5)
        data = stats.model_dump()
        assert data["goals_scored"] == 10
        assert data["assists"] == 5
        assert data["goal_value"] == 12.5

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"goals_scored": 10, "assists": 5, "goal_value": 12.5}
        stats = PlayerStats.model_validate(data)
        assert stats.goals_scored == 10
        assert stats.assists == 5
        assert stats.goal_value == 12.5


class TestSeasonData:
    """Test SeasonData schema validation."""

    def test_creates_with_required_fields(
        self,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test creating SeasonData with required fields."""
        season_data = SeasonData(
            season=sample_season_display,
            team=sample_team_info,
            competition=sample_competition_info,
            league_rank=None,
            stats=empty_player_stats,
        )

        assert season_data.season.id == 1
        assert season_data.team.id == 1
        assert season_data.competition.id == 1
        assert season_data.league_rank is None

    def test_creates_with_league_rank(
        self,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test creating SeasonData with league_rank."""
        season_data = SeasonData(
            season=sample_season_display,
            team=sample_team_info,
            competition=sample_competition_info,
            stats=empty_player_stats,
            league_rank=1,
        )

        assert season_data.league_rank == 1

    def test_requires_season(
        self,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test that season is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonData(
                team=sample_team_info, competition=sample_competition_info, stats=empty_player_stats
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("season",) for error in errors)

    def test_requires_team(
        self,
        sample_season_display: SeasonDisplay,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test that team is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonData(
                season=sample_season_display,
                competition=sample_competition_info,
                stats=empty_player_stats,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("team",) for error in errors)

    def test_requires_competition(
        self,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test that competition is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonData(
                season=sample_season_display, team=sample_team_info, stats=empty_player_stats
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("competition",) for error in errors)

    def test_requires_stats(
        self,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
    ) -> None:
        """Test that stats is required."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonData(
                season=sample_season_display,
                team=sample_team_info,
                competition=sample_competition_info,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("stats",) for error in errors)

    def test_validates_league_rank_type(
        self,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test that league_rank must be an integer."""
        with pytest.raises(ValidationError) as exc_info:
            SeasonData(
                season=sample_season_display,
                team=sample_team_info,
                competition=sample_competition_info,
                stats=empty_player_stats,
                league_rank="not_int",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("league_rank",) for error in errors)

    def test_serializes_to_dict(
        self,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test serialization to dictionary."""
        season_data = SeasonData(
            season=sample_season_display,
            team=sample_team_info,
            competition=sample_competition_info,
            league_rank=1,
            stats=empty_player_stats,
        )
        data = season_data.model_dump()
        assert data["season"]["id"] == 1
        assert data["team"]["id"] == 1
        assert data["competition"]["id"] == 1
        assert data["league_rank"] == 1

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "season": {"id": 1, "start_year": 2023, "end_year": None, "display_name": "2023-24"},
            "team": {"id": 1, "name": "Barcelona"},
            "competition": {"id": 1, "name": "La Liga"},
            "league_rank": 1,
            "stats": {},
        }
        season_data = SeasonData.model_validate(data)
        assert season_data.season.id == 1
        assert season_data.team.id == 1
        assert season_data.competition.id == 1
        assert season_data.league_rank == 1


class TestPlayerDetailsResponse:
    """Test PlayerDetailsResponse schema validation."""

    def test_creates_with_nested_models(
        self,
        sample_player_info: PlayerInfo,
        sample_season_display: SeasonDisplay,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
    ) -> None:
        """Test creating PlayerDetailsResponse with nested models."""
        stats = PlayerStats(goals_scored=10)

        season_data = SeasonData(
            season=sample_season_display,
            team=sample_team_info,
            competition=sample_competition_info,
            league_rank=None,
            stats=stats,
        )

        career_totals = CareerTotals(
            total_goal_value=10.5,
            goal_value_avg=1.05,
            total_goals=10,
            total_assists=5,
            total_matches_played=30,
        )
        response = PlayerDetailsResponse(
            player=sample_player_info, seasons=[season_data], career_totals=career_totals
        )

        assert response.player.id == 1
        assert len(response.seasons) == 1
        assert response.seasons[0].stats.goals_scored == 10
        assert response.career_totals.total_goals == 10

    def test_requires_player(self) -> None:
        """Test that player is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerDetailsResponse(seasons=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("player",) for error in errors)

    def test_requires_seasons(self, sample_player_info: PlayerInfo) -> None:
        """Test that seasons is required."""
        career_totals = CareerTotals(
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_assists=0,
            total_matches_played=0,
        )
        with pytest.raises(ValidationError) as exc_info:
            PlayerDetailsResponse(player=sample_player_info, career_totals=career_totals)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("seasons",) for error in errors)

    def test_accepts_empty_seasons_list(self, sample_player_info: PlayerInfo) -> None:
        """Test that empty seasons list is accepted."""
        career_totals = CareerTotals(
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_assists=0,
            total_matches_played=0,
        )
        response = PlayerDetailsResponse(
            player=sample_player_info, seasons=[], career_totals=career_totals
        )
        assert response.seasons == []

    def test_accepts_multiple_seasons(
        self,
        sample_player_info: PlayerInfo,
        sample_team_info: TeamInfo,
        sample_competition_info: CompetitionInfo,
        empty_player_stats: PlayerStats,
    ) -> None:
        """Test that multiple seasons can be provided."""
        season1 = SeasonDisplay(id=1, start_year=2023, end_year=None, display_name="2023-24")
        season2 = SeasonDisplay(id=2, start_year=2024, end_year=None, display_name="2024-25")

        season_data1 = SeasonData(
            season=season1,
            team=sample_team_info,
            competition=sample_competition_info,
            league_rank=None,
            stats=empty_player_stats,
        )
        season_data2 = SeasonData(
            season=season2,
            team=sample_team_info,
            competition=sample_competition_info,
            league_rank=None,
            stats=empty_player_stats,
        )

        career_totals = CareerTotals(
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_assists=0,
            total_matches_played=0,
        )
        response = PlayerDetailsResponse(
            player=sample_player_info,
            seasons=[season_data1, season_data2],
            career_totals=career_totals,
        )

        assert len(response.seasons) == 2

    def test_validates_seasons_list_type(self, sample_player_info: PlayerInfo) -> None:
        """Test that seasons must be a list."""
        career_totals = CareerTotals(
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_assists=0,
            total_matches_played=0,
        )
        with pytest.raises(ValidationError) as exc_info:
            PlayerDetailsResponse(
                player=sample_player_info, seasons="not_a_list", career_totals=career_totals
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("seasons",) for error in errors)

    def test_serializes_to_dict(self, sample_player_info: PlayerInfo) -> None:
        """Test serialization to dictionary."""
        career_totals = CareerTotals(
            total_goal_value=0.0,
            goal_value_avg=0.0,
            total_goals=0,
            total_assists=0,
            total_matches_played=0,
        )
        response = PlayerDetailsResponse(
            player=sample_player_info, seasons=[], career_totals=career_totals
        )
        data = response.model_dump()
        assert data["player"]["id"] == 1
        assert data["seasons"] == []
        assert "career_totals" in data

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "player": {"id": 1, "name": "Lionel Messi", "nation": None},
            "seasons": [],
            "career_totals": {
                "total_goal_value": 10.5,
                "goal_value_avg": 1.05,
                "total_goals": 10,
                "total_assists": 5,
                "total_matches_played": 30,
            },
        }
        response = PlayerDetailsResponse.model_validate(data)
        assert response.player.id == 1
        assert response.player.name == "Lionel Messi"
        assert response.seasons == []
        assert response.career_totals.total_goals == 10
