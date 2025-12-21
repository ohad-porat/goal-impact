"""Integration tests for leaders router endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.models.player_stats import PlayerStats
from app.tests.utils.factories import (
    PlayerFactory,
    PlayerStatsFactory,
    TeamFactory,
)
from app.tests.utils.helpers import (
    assert_422_validation_error,
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

    def test_response_structure_is_correct(self, client: TestClient, db_session) -> None:
        """Test that response structure matches the expected schema."""
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

        response = client.get("/api/v1/leaders/career-totals")

        assert response.status_code == 200
        data = response.json()
        assert "top_goal_value" in data
        assert isinstance(data["top_goal_value"], list)

        if len(data["top_goal_value"]) > 0:
            player_data = data["top_goal_value"][0]
            assert "player_id" in player_data
            assert "player_name" in player_data
            assert "nation" in player_data
            assert "total_goal_value" in player_data
            assert "goal_value_avg" in player_data
            assert "total_goals" in player_data
            assert "total_matches" in player_data
            assert isinstance(player_data["player_id"], int)
            assert isinstance(player_data["total_goal_value"], float)

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

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["top_goal_value"] == []

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

    def test_response_structure_is_correct(self, client: TestClient, db_session) -> None:
        """Test that response structure matches the expected schema."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=30.0,
            goals_scored=12,
            matches_played=25,
        )
        db_session.commit()

        response = client.get(f"/api/v1/leaders/by-season?season_id={season.id}")

        assert response.status_code == 200
        data = response.json()
        assert "top_goal_value" in data
        assert isinstance(data["top_goal_value"], list)

        if len(data["top_goal_value"]) > 0:
            player_data = data["top_goal_value"][0]
            assert "player_id" in player_data
            assert "player_name" in player_data
            assert "clubs" in player_data
            assert "total_goal_value" in player_data
            assert "goal_value_avg" in player_data
            assert "total_goals" in player_data
            assert "total_matches" in player_data
            assert isinstance(player_data["player_id"], int)
            assert isinstance(player_data["total_goal_value"], float)
            assert isinstance(player_data["clubs"], str)

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

    def test_handles_various_invalid_season_id_types(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid season_id types return validation error."""
        assert_invalid_id_types_return_422(
            client, "/api/v1/leaders/by-season?season_id={invalid_id}"
        )

    def test_handles_various_invalid_league_id_types(
        self, client: TestClient, db_session
    ) -> None:
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
