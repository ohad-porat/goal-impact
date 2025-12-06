"""Integration tests for players router endpoints."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    MatchFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    TeamFactory,
)
from app.tests.utils.helpers import (
    assert_404_not_found,
    assert_422_validation_error,
    create_basic_season_setup,
    create_goal_event,
    create_match_with_goal,
)


class TestGetPlayerDetailsRoute:
    """Tests for GET /api/v1/players/{player_id} endpoint."""

    def test_returns_404_when_player_not_found(self, client: TestClient, db_session):
        """Test that 404 is returned when player doesn't exist."""
        assert_404_not_found(client, "/api/v1/players/99999")

    def test_returns_player_details_successfully(self, client: TestClient, db_session):
        """Test that player details are returned with correct structure."""
        player = PlayerFactory(name="Test Player")
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}")

        assert response.status_code == 200
        data = response.json()
        assert "player" in data
        assert "seasons" in data
        assert data["player"]["id"] == player.id
        assert data["player"]["name"] == "Test Player"
        assert isinstance(data["seasons"], list)

    def test_returns_player_with_seasons(self, client: TestClient, db_session):
        """Test that player with seasons returns correct data."""
        nation, comp, season = create_basic_season_setup(db_session)
        player = PlayerFactory(name="Star Player", nation=nation)
        team = TeamFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            team=team,
            season=season,
            matches_played=30,
            goals_scored=15,
            assists=10,
        )
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 1
        season_data = data["seasons"][0]
        assert "season" in season_data
        assert "team" in season_data
        assert "competition" in season_data
        assert "stats" in season_data
        assert season_data["stats"]["matches_played"] == 30
        assert season_data["stats"]["goals_scored"] == 15
        assert season_data["stats"]["assists"] == 10

    def test_returns_player_without_seasons(self, client: TestClient, db_session):
        """Test that player without seasons returns empty seasons list."""
        player = PlayerFactory(name="New Player")
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["player"]["id"] == player.id
        assert data["seasons"] == []

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema with all required fields."""
        nation = NationFactory(name="England", country_code="ENG")
        player = PlayerFactory(name="Test Player", nation=nation)
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}")

        assert response.status_code == 200
        data = response.json()

        assert "id" in data["player"]
        assert "name" in data["player"]
        assert "nation" in data["player"]
        assert isinstance(data["player"]["id"], int)
        assert isinstance(data["player"]["name"], str)

        assert isinstance(data["seasons"], list)

    @pytest.mark.parametrize("invalid_id", ["not-a-number", "abc", "12.5"])
    def test_handles_various_invalid_player_id_types(self, client: TestClient, db_session, invalid_id):
        """Test that various invalid player_id types return validation error."""
        assert_422_validation_error(client, f"/api/v1/players/{invalid_id}")

    def test_handles_negative_and_zero_player_id(self, client: TestClient, db_session):
        """Test that negative and zero player_id return 404 (valid integers but no resource)."""
        response_neg = client.get("/api/v1/players/-1")
        response_zero = client.get("/api/v1/players/0")
        assert response_neg.status_code == 404
        assert response_zero.status_code == 404

    def test_returns_multiple_seasons_sorted_correctly(self, client: TestClient, db_session):
        """Test that multiple seasons are returned sorted by start_year ascending."""
        nation, comp1, season1 = create_basic_season_setup(
            db_session, nation=None, start_year=2022, end_year=2023
        )
        _comp2 = comp1
        season2 = SeasonFactory(competition=_comp2, start_year=2023, end_year=2024)
        player = PlayerFactory(nation=nation)
        team1 = TeamFactory(nation=nation)
        team2 = TeamFactory(nation=nation)

        PlayerStatsFactory(player=player, team=team1, season=season1)
        PlayerStatsFactory(player=player, team=team2, season=season2)
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 2
        assert data["seasons"][0]["season"]["start_year"] == 2022
        assert data["seasons"][1]["season"]["start_year"] == 2023


class TestGetPlayerCareerGoalLogRoute:
    """Tests for GET /api/v1/players/{player_id}/goals endpoint."""

    def test_returns_404_when_player_not_found(self, client: TestClient, db_session):
        """Test that 404 is returned when player doesn't exist."""
        assert_404_not_found(client, "/api/v1/players/99999/goals")

    def test_returns_empty_goals_when_player_has_no_goals(self, client: TestClient, db_session):
        """Test that empty goals list is returned when player has no goal events."""
        player = PlayerFactory(name="No Goals Player")
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert "player" in data
        assert "goals" in data
        assert data["player"]["id"] == player.id
        assert data["goals"] == []

    def test_returns_player_goals_successfully(self, client: TestClient, db_session):
        """Test that player goals are returned with correct structure."""
        _match, player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=5.5, minute=45, match_date=date(2024, 3, 15)
        )

        response = client.get(f"/api/v1/players/{player.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert data["player"]["id"] == player.id
        assert len(data["goals"]) == 1
        goal = data["goals"][0]
        assert "minute" in goal
        assert "goal_value" in goal
        assert goal["minute"] == 45
        assert goal["goal_value"] == 5.5

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        _match, player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=3.5, minute=10, match_date=date(2024, 1, 1)
        )

        response = client.get(f"/api/v1/players/{player.id}/goals")

        assert response.status_code == 200
        data = response.json()

        assert "id" in data["player"]
        assert "name" in data["player"]
        assert isinstance(data["player"]["id"], int)

        assert isinstance(data["goals"], list)
        if len(data["goals"]) > 0:
            goal = data["goals"][0]
            assert "minute" in goal
            assert "goal_value" in goal
            assert "team" in goal
            assert "opponent" in goal
            assert "date" in goal
            assert "venue" in goal
            assert "score_before" in goal
            assert "score_after" in goal

    def test_returns_goals_with_assists(self, client: TestClient, db_session):
        """Test that goals with assists include assist information."""
        _match, player, _team, _season, assister = create_match_with_goal(
            db_session, goal_value=4.0, minute=15, with_assist=True, match_date=date(2024, 1, 1)
        )

        response = client.get(f"/api/v1/players/{player.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        goal = data["goals"][0]
        assert "assisted_by" in goal
        assert goal["assisted_by"] is not None
        assert goal["assisted_by"]["name"] == assister.name

    def test_returns_goals_without_assists(self, client: TestClient, db_session):
        """Test that goals without assists have null assisted_by."""
        _match, player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=3.0, minute=20, match_date=date(2024, 1, 1)
        )

        response = client.get(f"/api/v1/players/{player.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        goal = data["goals"][0]
        assert goal.get("assisted_by") is None

    @pytest.mark.parametrize("invalid_id", ["not-a-number", "abc", "12.5"])
    def test_handles_various_invalid_player_id_types_for_goals(self, client: TestClient, db_session, invalid_id):
        """Test that various invalid player_id types return validation error for goals endpoint."""
        assert_422_validation_error(client, f"/api/v1/players/{invalid_id}/goals")

    def test_handles_negative_and_zero_player_id_for_goals(self, client: TestClient, db_session):
        """Test that negative and zero player_id return 404 for goals endpoint."""
        response_neg = client.get("/api/v1/players/-1/goals")
        response_zero = client.get("/api/v1/players/0/goals")
        assert response_neg.status_code == 404
        assert response_zero.status_code == 404

    def test_returns_goals_sorted_by_date(self, client: TestClient, db_session):
        """Test that goals are returned sorted by date (earliest first, then by minute)."""
        nation, comp, season = create_basic_season_setup(db_session)
        player = PlayerFactory(nation=nation)
        team = TeamFactory(nation=nation)
        opponent1 = TeamFactory(nation=nation)
        opponent2 = TeamFactory(nation=nation)

        match1 = MatchFactory(
            season=season,
            home_team=team,
            away_team=opponent1,
            date=date(2024, 1, 1),
        )
        match2 = MatchFactory(
            season=season,
            home_team=team,
            away_team=opponent2,
            date=date(2024, 3, 15),
        )

        create_goal_event(
            match1,
            player,
            minute=10,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=2.0,
        )
        create_goal_event(
            match2,
            player,
            minute=20,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=3.0,
        )
        db_session.commit()

        response = client.get(f"/api/v1/players/{player.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 2
        assert data["goals"][0]["date"] == "01/01/2024"
        assert data["goals"][0]["minute"] == 10
        assert data["goals"][1]["date"] == "15/03/2024"
        assert data["goals"][1]["minute"] == 20
