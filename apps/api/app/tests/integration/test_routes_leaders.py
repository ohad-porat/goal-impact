"""Integration tests for leaders router endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.models.player_stats import PlayerStats
from app.tests.utils.factories import (
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    TeamFactory,
)
from app.tests.utils.helpers import (
    assert_empty_list_response,
    assert_invalid_id_types_return_422,
    create_basic_season_setup,
    create_two_competitions_with_data,
)


class TestGetCareerTotalsLeadersRoute:
    """Tests for GET /api/v1/leaders/career-totals endpoint."""

    def test_returns_empty_list_when_no_players(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no players exist for career totals."""
        assert_empty_list_response(client, "/api/v1/leaders/career-totals", "top_goal_value")

    def test_returns_career_totals_successfully(self, client: TestClient, db_session) -> None:
        """Test that career totals are returned with correct structure."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(name="Top Player", nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=50.5,
            goals_scored=20,
            matches_played=30,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/career-totals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_name"] == "Top Player"
        assert data["top_goal_value"][0]["total_goal_value"] == 50.5

    def test_uses_default_limit_of_50(self, client: TestClient, db_session) -> None:
        """Test that default limit of 50 is used when not specified."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(60):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )
        db_session.commit()

        response = client.get("/api/v1/leaders/career-totals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 50

    def test_respects_limit_parameter(self, client: TestClient, db_session) -> None:
        """Test that limit parameter is respected."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )
        db_session.commit()

        response = client.get("/api/v1/leaders/career-totals?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 5

    @pytest.mark.parametrize(
        "limit,expected_status",
        [
            (0, 422),
            (101, 422),
            (1, 200),
            (100, 200),
        ],
    )
    def test_validates_limit(self, client: TestClient, db_session, limit, expected_status) -> None:
        """Test that limit validation works correctly."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/career-totals?limit={limit}")
        assert response.status_code == expected_status
        if expected_status == 200:
            data = response.json()
            assert "top_goal_value" in data

    def test_filters_by_league_id(self, client: TestClient, db_session) -> None:
        """Test that league_id query parameter filters results correctly."""

        def create_player_data(season, nation):
            team = TeamFactory(nation=nation)
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=50.0 if season.competition.name == "Premier League" else 40.0,
                goals_scored=20 if season.competition.name == "Premier League" else 15,
                matches_played=30 if season.competition.name == "Premier League" else 25,
            )
            return player

        comp1, _comp2, player1, _player2, _nation = create_two_competitions_with_data(
            db_session, create_player_data
        )

        response = client.get(f"/api/v1/leaders/career-totals?league_id={comp1.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_id"] == player1.id

    def test_league_id_parameter_is_optional(self, client: TestClient, db_session) -> None:
        """Test that league_id parameter is optional."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=30.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/career-totals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1

    def test_handles_invalid_league_id_gracefully(self, client: TestClient, db_session) -> None:
        """Test that invalid league_id returns empty list without errors."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/career-totals?league_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["top_goal_value"] == []


class TestGetBySeasonLeadersRoute:
    """Tests for GET /api/v1/leaders/by-season endpoint."""

    def test_requires_season_id_parameter(self, client: TestClient, db_session) -> None:
        """Test that season_id parameter is required."""
        response = client.get("/api/v1/leaders/by-season")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_returns_empty_list_when_no_players(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no players exist for season."""
        nation, comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_empty_list_response(
            client, f"/api/v1/leaders/by-season?season_id={season.id}", "top_goal_value"
        )

    def test_returns_by_season_leaders_successfully(self, client: TestClient, db_session) -> None:
        """Test that by-season leaders are returned with correct structure."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(name="Season Leader", nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=45.5,
            goals_scored=18,
            matches_played=28,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_name"] == "Season Leader"
        assert data["top_goal_value"][0]["total_goal_value"] == 45.5

    def test_uses_default_limit_of_50(self, client: TestClient, db_session) -> None:
        """Test that default limit of 50 is used when not specified."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(60):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 50

    def test_respects_limit_parameter(self, client: TestClient, db_session) -> None:
        """Test that limit parameter is respected."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 5

    @pytest.mark.parametrize(
        "limit,expected_status",
        [
            (0, 422),
            (101, 422),
            (1, 200),
            (100, 200),
        ],
    )
    def test_validates_limit(self, client: TestClient, db_session, limit, expected_status) -> None:
        """Test that limit validation works correctly."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}&limit={limit}")
        assert response.status_code == expected_status
        if expected_status == 200:
            data = response.json()
            assert "top_goal_value" in data

    def test_filters_by_league_id(self, client: TestClient, db_session) -> None:
        """Test that league_id query parameter filters results correctly."""

        def create_player_data(season, nation):
            team = TeamFactory(nation=nation)
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=40.0 if season.competition.name == "Premier League" else 35.0,
                goals_scored=15 if season.competition.name == "Premier League" else 12,
                matches_played=25 if season.competition.name == "Premier League" else 22,
            )
            return player

        comp1, _comp2, player1, _player2, _nation = create_two_competitions_with_data(
            db_session, create_player_data
        )
        player_stats = (
            db_session.query(PlayerStats).filter(PlayerStats.player_id == player1.id).first()
        )
        assert player_stats is not None, "Player stats should exist"
        season1 = player_stats.season

        response = client.get(
            f"/api/v1/leaders/by-season?season_id={season1.id}&league_id={comp1.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_id"] == player1.id

    def test_league_id_parameter_is_optional(self, client: TestClient, db_session) -> None:
        """Test that league_id parameter is optional."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1

    def test_handles_various_invalid_season_id_types(self, client: TestClient, db_session) -> None:
        """Test that various invalid season_id types return validation error."""
        assert_invalid_id_types_return_422(
            client, "/api/v1/leaders/by-season?season_id={invalid_id}"
        )

    def test_handles_various_invalid_league_id_types(self, client: TestClient, db_session) -> None:
        """Test that various invalid league_id types return validation error."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, "/api/v1/leaders/career-totals?league_id={invalid_id}"
        )
        assert_invalid_id_types_return_422(
            client, f"/api/v1/leaders/by-season?season_id={season.id}&league_id={{invalid_id}}"
        )

    def test_handles_invalid_league_id_gracefully(self, client: TestClient, db_session) -> None:
        """Test that invalid league_id returns empty list without errors for by-season endpoint."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=20.0,
            goals_scored=8,
            matches_played=15,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}&league_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["top_goal_value"] == []


class TestGetAllSeasonsLeadersRoute:
    """Tests for GET /api/v1/leaders/all-seasons endpoint."""

    def test_returns_empty_list_when_no_players(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no players exist for all seasons."""
        assert_empty_list_response(client, "/api/v1/leaders/all-seasons", "top_goal_value")

    def test_returns_all_seasons_leaders_successfully(self, client: TestClient, db_session) -> None:
        """Test that all-seasons leaders are returned with correct structure."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(name="All Seasons Leader", nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=45.5,
            goals_scored=18,
            matches_played=28,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_name"] == "All Seasons Leader"
        assert data["top_goal_value"][0]["total_goal_value"] == 45.5
        assert "season_id" in data["top_goal_value"][0]
        assert "season_display_name" in data["top_goal_value"][0]
        assert "clubs" in data["top_goal_value"][0]
        assert data["top_goal_value"][0]["clubs"] == team.name

    def test_uses_default_limit_of_50(self, client: TestClient, db_session) -> None:
        """Test that default limit of 50 is used when not specified."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(60):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 50

        values = [p["total_goal_value"] for p in data["top_goal_value"]]
        assert values == sorted(values, reverse=True)
        assert values[0] == 60.0
        assert values[-1] == 11.0

    def test_respects_limit_parameter(self, client: TestClient, db_session) -> None:
        """Test that limit parameter is respected."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 5

        values = [p["total_goal_value"] for p in data["top_goal_value"]]
        assert values == sorted(values, reverse=True)
        assert values[0] == 10.0
        assert values[-1] == 6.0

    @pytest.mark.parametrize(
        "limit,expected_status",
        [
            (0, 422),
            (101, 422),
            (1, 200),
            (100, 200),
        ],
    )
    def test_validates_limit(self, client: TestClient, db_session, limit, expected_status) -> None:
        """Test that limit validation works correctly."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/all-seasons?limit={limit}")
        assert response.status_code == expected_status
        if expected_status == 200:
            data = response.json()
            assert "top_goal_value" in data

    def test_filters_by_league_id(self, client: TestClient, db_session) -> None:
        """Test that league_id query parameter filters results correctly."""

        def create_player_data(season, nation):
            team = TeamFactory(nation=nation)
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=50.0 if season.competition.name == "Premier League" else 40.0,
                goals_scored=20 if season.competition.name == "Premier League" else 15,
                matches_played=30 if season.competition.name == "Premier League" else 25,
            )
            return player

        comp1, _comp2, player1, _player2, _nation = create_two_competitions_with_data(
            db_session, create_player_data
        )

        response = client.get(f"/api/v1/leaders/all-seasons?league_id={comp1.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["player_id"] == player1.id

    def test_league_id_parameter_is_optional(self, client: TestClient, db_session) -> None:
        """Test that league_id parameter is optional."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=30.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1

    def test_handles_invalid_league_id_gracefully(self, client: TestClient, db_session) -> None:
        """Test that invalid league_id returns empty list without errors."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons?league_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["top_goal_value"] == []

    def test_handles_various_invalid_league_id_types(self, client: TestClient, db_session) -> None:
        """Test that various invalid league_id types return validation error."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, "/api/v1/leaders/all-seasons?league_id={invalid_id}"
        )

    def test_returns_same_player_multiple_times_for_different_seasons(
        self, client: TestClient, db_session
    ) -> None:
        """Test that same player can appear multiple times for different seasons."""
        nation, comp, season1 = create_basic_season_setup(
            db_session, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(name="Multi Season Player", nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season1,
            team=team,
            goal_value=15.0,
            goals_scored=7,
            matches_played=12,
        )
        PlayerStatsFactory(
            player=player,
            season=season2,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 2
        assert all(p["player_name"] == "Multi Season Player" for p in data["top_goal_value"])
        assert data["top_goal_value"][0]["season_id"] == season1.id
        assert data["top_goal_value"][0]["total_goal_value"] == 15.0
        assert data["top_goal_value"][1]["season_id"] == season2.id
        assert data["top_goal_value"][1]["total_goal_value"] == 10.0

    def test_includes_season_display_name_in_response(self, client: TestClient, db_session) -> None:
        """Test that season_display_name is included in response."""
        nation, comp, season = create_basic_season_setup(db_session, start_year=2022, end_year=2023)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=25.0,
            goals_scored=10,
            matches_played=20,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["season_display_name"] == "2022/2023"
        assert data["top_goal_value"][0]["season_id"] == season.id

    def test_aggregates_stats_across_multiple_teams_in_same_season(
        self, client: TestClient, db_session
    ) -> None:
        """Test that stats are aggregated across multiple teams in same season."""
        nation, comp, season = create_basic_season_setup(db_session)
        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Chelsea", nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team1,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team2,
            goal_value=7.5,
            goals_scored=3,
            matches_played=6,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 1
        assert data["top_goal_value"][0]["total_goal_value"] == 12.5
        assert data["top_goal_value"][0]["total_goals"] == 5
        assert data["top_goal_value"][0]["total_matches"] == 11
        clubs = data["top_goal_value"][0]["clubs"]
        assert "Arsenal" in clubs
        assert "Chelsea" in clubs

    def test_sorts_by_goal_value_avg_as_secondary_sort(
        self, client: TestClient, db_session
    ) -> None:
        """Test that secondary sort by goal_value_avg works correctly (descending)."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season,
            team=team,
            goal_value=10.0,
            goals_scored=4,
            matches_played=10,
        )
        db_session.commit()

        response = client.get("/api/v1/leaders/all-seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["top_goal_value"]) == 2
        assert data["top_goal_value"][0]["total_goal_value"] == 10.0
        assert data["top_goal_value"][0]["goal_value_avg"] == 2.5
        assert data["top_goal_value"][1]["total_goal_value"] == 10.0
        assert data["top_goal_value"][1]["goal_value_avg"] == 2.0
