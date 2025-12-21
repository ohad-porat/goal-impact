"""Integration tests for home router endpoints."""

from datetime import date

from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    MatchFactory,
    PlayerFactory,
    TeamFactory,
)
from app.tests.utils.helpers import (
    assert_empty_list_response,
    assert_invalid_id_types_return_422,
    create_basic_season_setup,
    create_goal_event,
    create_match_with_goal,
    create_two_competitions_with_data,
)


class TestGetRecentImpactGoalsRoute:
    """Tests for GET /api/v1/home/recent-goals endpoint."""

    def test_returns_empty_list_when_no_goals(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no goals exist."""
        assert_empty_list_response(client, "/api/v1/home/recent-goals", "goals")

    def test_returns_recent_goals_successfully(self, client: TestClient, db_session) -> None:
        """Test that recent goals are returned with correct structure."""
        _match, player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=5.5, minute=45
        )

        response = client.get("/api/v1/home/recent-goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["scorer"]["name"] == player.name
        assert data["goals"][0]["scorer"]["id"] == player.id
        assert data["goals"][0]["goal_value"] == 5.5
        assert data["goals"][0]["minute"] == 45
        assert "match" in data["goals"][0]
        assert "score_before" in data["goals"][0]
        assert "score_after" in data["goals"][0]

    def test_response_structure_is_correct(self, client: TestClient, db_session) -> None:
        """Test that response structure matches the expected schema."""
        _match, player, team, _season, _ = create_match_with_goal(
            db_session, goal_value=6.5, minute=30, home_pre=1, home_post=2
        )

        response = client.get("/api/v1/home/recent-goals")

        assert response.status_code == 200
        data = response.json()
        goal = data["goals"][0]

        assert "home_team" in goal["match"]
        assert "away_team" in goal["match"]
        assert "date" in goal["match"]
        assert goal["match"]["home_team"] == team.name

        assert "id" in goal["scorer"]
        assert "name" in goal["scorer"]
        assert goal["scorer"]["name"] == player.name

        assert isinstance(goal["minute"], int)
        assert isinstance(goal["goal_value"], float)
        assert isinstance(goal["score_before"], str)
        assert isinstance(goal["score_after"], str)

    def test_filters_by_league_id(self, client: TestClient, db_session) -> None:
        """Test that league_id query parameter filters results correctly."""

        def create_goal_data(season, nation):
            home_team = TeamFactory(nation=nation)
            away_team = TeamFactory(nation=nation)
            player = PlayerFactory(nation=nation, name=f"Player {season.competition.name}")
            match = MatchFactory(
                home_team=home_team,
                away_team=away_team,
                season=season,
                date=date.today(),
            )
            create_goal_event(
                match,
                player,
                10 if season.competition.name == "Premier League" else 20,
                0,
                1,
                0,
                0,
                goal_value=5.5 if season.competition.name == "Premier League" else 8.2,
            )
            return player

        comp1, _comp2, player1, _player2, _nation = create_two_competitions_with_data(
            db_session, create_goal_data
        )

        response = client.get(f"/api/v1/home/recent-goals?league_id={comp1.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["scorer"]["name"] == player1.name

    def test_league_id_parameter_is_optional(self, client: TestClient, db_session) -> None:
        """Test that league_id parameter is optional."""
        _match, _player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=5.5, minute=10
        )

        response = client.get("/api/v1/home/recent-goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1

    def test_returns_top_5_goals_sorted_by_goal_value(self, client: TestClient, db_session) -> None:
        """Test that results are limited to top 5 and sorted by goal_value descending."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)

        match_date = date.today()
        match = MatchFactory(
            home_team=home_team, away_team=away_team, season=season, date=match_date
        )

        for i in range(7):
            player = PlayerFactory(nation=nation)
            create_goal_event(match, player, 10 + i, 0, 1, 0, 0, goal_value=float(i))

        db_session.commit()

        response = client.get("/api/v1/home/recent-goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 5
        assert data["goals"][0]["goal_value"] == 6.0
        assert data["goals"][4]["goal_value"] == 2.0
        goal_values = [g["goal_value"] for g in data["goals"]]
        assert goal_values == sorted(goal_values, reverse=True)

    def test_handles_invalid_league_id_gracefully(self, client: TestClient, db_session) -> None:
        """Test that invalid league_id returns empty list without errors."""
        _match, _player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=5.5, minute=10
        )

        response = client.get("/api/v1/home/recent-goals?league_id=99999")

        assert response.status_code == 200
        data = response.json()
        assert data["goals"] == []

    def test_handles_various_invalid_league_id_types(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid league_id types return validation error."""
        assert_invalid_id_types_return_422(
            client, "/api/v1/home/recent-goals?league_id={invalid_id}"
        )
