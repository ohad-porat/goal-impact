"""Integration tests for clubs router endpoints."""

from datetime import date

from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.tests.utils.helpers import (
    assert_404_not_found,
    assert_empty_list_response,
    assert_invalid_id_types_return_422,
    create_basic_season_setup,
    create_match_with_goal,
)


class TestGetClubsByNationRoute:
    """Tests for GET /api/v1/clubs/ endpoint."""

    def test_returns_empty_list_when_no_clubs(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no clubs exist."""
        assert_empty_list_response(client, "/api/v1/clubs/", "nations")

    def test_returns_clubs_by_nation_successfully(self, client: TestClient, db_session) -> None:
        """Test that clubs grouped by nation are returned."""
        nation = NationFactory(name="England", country_code="ENG")
        comp = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        team = TeamFactory(name="Arsenal FC", nation=nation)
        TeamStatsFactory(team=team, season=season, ranking=1)
        db_session.commit()

        response = client.get("/api/v1/clubs/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["nations"]) >= 1
        nation_data = next((n for n in data["nations"] if n["nation"]["name"] == "England"), None)
        assert nation_data is not None
        assert len(nation_data["clubs"]) >= 1


class TestGetClubDetailsRoute:
    """Tests for GET /api/v1/clubs/{club_id} endpoint."""

    def test_returns_404_when_club_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when club doesn't exist."""
        assert_404_not_found(client, "/api/v1/clubs/99999")

    def test_returns_club_details_successfully(self, client: TestClient, db_session) -> None:
        """Test that club details are returned with correct structure."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Test Club", nation=nation)
        TeamStatsFactory(team=team, season=season, ranking=1)
        db_session.commit()

        response = client.get(f"/api/v1/clubs/{team.id}")

        assert response.status_code == 200
        data = response.json()
        assert "club" in data
        assert "seasons" in data
        assert data["club"]["id"] == team.id
        assert data["club"]["name"] == "Test Club"

    def test_returns_club_with_seasons(self, client: TestClient, db_session) -> None:
        """Test that club with seasons returns correct data."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        TeamStatsFactory(
            team=team,
            season=season,
            ranking=1,
            matches_played=38,
            wins=30,
            draws=5,
            losses=3,
        )
        db_session.commit()

        response = client.get(f"/api/v1/clubs/{team.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 1
        season_data = data["seasons"][0]
        assert "season" in season_data
        assert "competition" in season_data
        assert "stats" in season_data
        assert season_data["stats"]["matches_played"] == 38
        assert season_data["stats"]["wins"] == 30

    def test_returns_club_without_seasons(self, client: TestClient, db_session) -> None:
        """Test that club without seasons returns empty seasons list."""
        nation = NationFactory()
        team = TeamFactory(nation=nation)
        db_session.commit()

        response = client.get(f"/api/v1/clubs/{team.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["club"]["id"] == team.id
        assert data["seasons"] == []

    def test_handles_various_invalid_club_id_types(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid club_id types return validation error."""
        assert_invalid_id_types_return_422(client, "/api/v1/clubs/{invalid_id}")


class TestGetTeamSeasonSquadRoute:
    """Tests for GET /api/v1/clubs/{team_id}/seasons/{season_id} endpoint."""

    def test_returns_404_when_team_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when team doesn't exist."""
        nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/clubs/99999/seasons/{season.id}", "team")

    def test_returns_404_when_season_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when season doesn't exist."""
        nation, comp, _season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/clubs/{team.id}/seasons/99999", "season")

    def test_returns_empty_squad_when_season_exists_but_team_has_no_stats(
        self, client: TestClient, db_session
    ) -> None:
        """Test that empty squad is returned when season exists but team has no player stats for it."""
        nation, _comp1, season1 = create_basic_season_setup(db_session)
        team1 = TeamFactory(nation=nation)
        team2 = TeamFactory(nation=nation)
        PlayerStatsFactory(player=PlayerFactory(nation=nation), team=team1, season=season1)
        db_session.commit()

        response = client.get(f"/api/v1/clubs/{team2.id}/seasons/{season1.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["players"] == []
        assert data["season"]["id"] == season1.id

    def test_returns_team_season_squad_successfully(self, client: TestClient, db_session) -> None:
        """Test that team season squad is returned with correct structure."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Test Team", nation=nation)
        player = PlayerFactory(name="Test Player", nation=nation)

        PlayerStatsFactory(
            player=player,
            team=team,
            season=season,
            matches_played=30,
            goals_scored=15,
            assists=10,
        )
        db_session.commit()

        response = client.get(f"/api/v1/clubs/{team.id}/seasons/{season.id}")

        assert response.status_code == 200
        data = response.json()
        assert "team" in data
        assert "season" in data
        assert "competition" in data
        assert "players" in data
        assert data["team"]["id"] == team.id
        assert data["season"]["id"] == season.id
        assert len(data["players"]) == 1

    def test_returns_empty_squad_when_no_players(self, client: TestClient, db_session) -> None:
        """Test that empty squad is returned when team has no players for season."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        db_session.commit()

        assert_empty_list_response(
            client, f"/api/v1/clubs/{team.id}/seasons/{season.id}", "players"
        )

    def test_handles_various_invalid_team_id_types(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid team_id types return validation error."""
        nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, f"/api/v1/clubs/{{invalid_id}}/seasons/{season.id}"
        )

    def test_handles_various_invalid_season_id_types(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid season_id types return validation error."""
        nation, comp, _season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, f"/api/v1/clubs/{team.id}/seasons/{{invalid_id}}"
        )


class TestGetTeamSeasonGoalLogRoute:
    """Tests for GET /api/v1/clubs/{team_id}/seasons/{season_id}/goals endpoint."""

    def test_returns_404_when_team_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when team doesn't exist."""
        nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/clubs/99999/seasons/{season.id}/goals", "team")

    def test_returns_404_when_season_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when season doesn't exist."""
        nation, comp, _season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/clubs/{team.id}/seasons/99999/goals", "season")

    def test_returns_empty_goals_when_season_exists_but_team_has_no_goals(
        self, client: TestClient, db_session
    ) -> None:
        """Test that empty goals list is returned when season exists but team has no goals for it."""
        nation, _comp1, season1 = create_basic_season_setup(db_session)
        _team1 = TeamFactory(nation=nation)
        team2 = TeamFactory(nation=nation)
        _match, _player, _team, _season, _ = create_match_with_goal(
            db_session, goal_value=5.5, minute=45, match_date=date(2024, 3, 15)
        )
        db_session.commit()

        response = client.get(f"/api/v1/clubs/{team2.id}/seasons/{season1.id}/goals")
        assert response.status_code == 200
        data = response.json()
        assert data["goals"] == []
        assert data["season"]["id"] == season1.id

    def test_returns_team_season_goal_log_successfully(
        self, client: TestClient, db_session
    ) -> None:
        """Test that team season goal log is returned with correct structure."""
        _match, _player, team, season, _ = create_match_with_goal(
            db_session, goal_value=5.5, minute=45, match_date=date(2024, 3, 15)
        )

        response = client.get(f"/api/v1/clubs/{team.id}/seasons/{season.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert "team" in data
        assert "season" in data
        assert "competition" in data
        assert "goals" in data
        assert data["team"]["id"] == team.id
        assert data["season"]["id"] == season.id
        assert len(data["goals"]) == 1

    def test_returns_empty_goals_when_no_goals(self, client: TestClient, db_session) -> None:
        """Test that empty goals list is returned when team has no goals for season."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        db_session.commit()

        assert_empty_list_response(
            client, f"/api/v1/clubs/{team.id}/seasons/{season.id}/goals", "goals"
        )

    def test_includes_assist_information(self, client: TestClient, db_session) -> None:
        """Test that goals with assists include assist information."""
        _match, _scorer, team, season, assister = create_match_with_goal(
            db_session, goal_value=4.0, minute=15, with_assist=True, match_date=date(2024, 1, 1)
        )

        response = client.get(f"/api/v1/clubs/{team.id}/seasons/{season.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        goal = data["goals"][0]
        assert "assisted_by" in goal
        assert goal["assisted_by"] is not None
        assert goal["assisted_by"]["name"] == assister.name

    def test_handles_various_invalid_team_id_types_for_goals(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid team_id types return validation error for goals endpoint."""
        nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, f"/api/v1/clubs/{{invalid_id}}/seasons/{season.id}/goals"
        )

    def test_handles_various_invalid_season_id_types_for_goals(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid season_id types return validation error for goals endpoint."""
        nation, comp, _season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, f"/api/v1/clubs/{team.id}/seasons/{{invalid_id}}/goals"
        )
