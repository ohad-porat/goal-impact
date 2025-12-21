"""Integration tests for leagues router endpoints."""

from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.tests.utils.helpers import (
    assert_404_not_found,
    assert_empty_list_response,
    assert_invalid_id_types_return_422,
    create_basic_season_setup,
)


class TestGetLeaguesRoute:
    """Tests for GET /api/v1/leagues/ endpoint."""

    def test_returns_empty_list_when_no_leagues(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no leagues exist."""
        assert_empty_list_response(client, "/api/v1/leagues/", "leagues")

    def test_returns_all_leagues_successfully(self, client: TestClient, db_session) -> None:
        """Test that all leagues are returned with correct structure."""
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")

        comp1 = CompetitionFactory(name="Premier League", nation=nation1, tier="1st")
        comp2 = CompetitionFactory(name="La Liga", nation=nation2, tier="1st")

        _season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        _season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get("/api/v1/leagues/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["leagues"]) >= 2
        league_names = [league_item["name"] for league_item in data["leagues"]]
        assert "Premier League" in league_names
        assert "La Liga" in league_names

    def test_includes_season_range(self, client: TestClient, db_session) -> None:
        """Test that available_seasons is included in response."""
        nation = NationFactory(name="England", country_code="ENG")
        comp = CompetitionFactory(name="Premier League", nation=nation)
        _season1 = SeasonFactory(competition=comp, start_year=2022, end_year=2023)
        _season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get("/api/v1/leagues/")

        assert response.status_code == 200
        data = response.json()
        league = next(
            (league_item for league_item in data["leagues"] if league_item["id"] == comp.id), None
        )
        assert league is not None
        assert "available_seasons" in league
        assert isinstance(league["available_seasons"], str)


class TestGetAllSeasonsRoute:
    """Tests for GET /api/v1/leagues/seasons endpoint."""

    def test_returns_empty_list_when_no_seasons(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when no seasons exist."""
        assert_empty_list_response(client, "/api/v1/leagues/seasons", "seasons")

    def test_returns_all_seasons_successfully(self, client: TestClient, db_session) -> None:
        """Test that all unique seasons are returned."""
        nation, comp, season1 = create_basic_season_setup(
            db_session, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get("/api/v1/leagues/seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) >= 2
        season_ids = [s["id"] for s in data["seasons"]]
        assert season1.id in season_ids
        assert season2.id in season_ids

    def test_sorts_by_start_year_descending(self, client: TestClient, db_session) -> None:
        """Test that seasons are sorted by start_year descending."""
        _nation, comp, _season1 = create_basic_season_setup(
            db_session, start_year=2022, end_year=2023
        )
        _season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        _season3 = SeasonFactory(competition=comp, start_year=2021, end_year=2022)
        db_session.commit()

        response = client.get("/api/v1/leagues/seasons")

        assert response.status_code == 200
        data = response.json()
        start_years = [s["start_year"] for s in data["seasons"]]
        assert start_years == sorted(start_years, reverse=True)


class TestGetLeagueSeasonsRoute:
    """Tests for GET /api/v1/leagues/{league_id}/seasons endpoint."""

    def test_returns_404_when_league_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when league doesn't exist."""
        assert_404_not_found(client, "/api/v1/leagues/99999/seasons")

    def test_returns_seasons_for_league_successfully(self, client: TestClient, db_session) -> None:
        """Test that seasons for a specific league are returned."""
        _nation, comp, season1 = create_basic_season_setup(
            db_session, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 2
        season_ids = [s["id"] for s in data["seasons"]]
        assert season1.id in season_ids
        assert season2.id in season_ids

    def test_returns_empty_list_when_no_seasons(self, client: TestClient, db_session) -> None:
        """Test that empty list is returned when league has no seasons."""
        nation = NationFactory()
        comp = CompetitionFactory(nation=nation)
        db_session.commit()

        assert_empty_list_response(client, f"/api/v1/leagues/{comp.id}/seasons", "seasons")

    def test_handles_various_invalid_league_id_types(self, client: TestClient, db_session) -> None:
        """Test that various invalid league_id types return validation error."""
        assert_invalid_id_types_return_422(client, "/api/v1/leagues/{invalid_id}/seasons")

    def test_only_returns_seasons_for_specified_league(
        self, client: TestClient, db_session
    ) -> None:
        """Test that only seasons for the specified league are returned."""
        nation1 = NationFactory()
        nation2 = NationFactory()
        comp1 = CompetitionFactory(nation=nation1)
        comp2 = CompetitionFactory(nation=nation2)

        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        _season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp1.id}/seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 1
        assert data["seasons"][0]["id"] == season1.id


class TestGetLeagueTableRoute:
    """Tests for GET /api/v1/leagues/{league_id}/table/{season_id} endpoint."""

    def test_returns_404_when_league_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when league doesn't exist."""
        _nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/leagues/99999/table/{season.id}", "league")

    def test_returns_404_when_season_not_found(self, client: TestClient, db_session) -> None:
        """Test that 404 is returned when season doesn't exist for league."""
        _nation, comp, _season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/leagues/{comp.id}/table/99999", "season")

    def test_returns_404_when_season_belongs_to_different_league(
        self, client: TestClient, db_session
    ) -> None:
        """Test that 404 is returned when season exists but belongs to different league."""
        nation, comp1, season1 = create_basic_season_setup(db_session)
        comp2 = CompetitionFactory(nation=nation)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/leagues/{comp1.id}/table/{season2.id}", "season")

    def test_returns_league_table_successfully(self, client: TestClient, db_session) -> None:
        """Test that league table is returned with correct structure."""
        nation, comp, season = create_basic_season_setup(db_session)
        team1 = TeamFactory(name="Team A", nation=nation)
        team2 = TeamFactory(name="Team B", nation=nation)

        TeamStatsFactory(team=team1, season=season, ranking=1, matches_played=38, points=90)
        TeamStatsFactory(team=team2, season=season, ranking=2, matches_played=38, points=85)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/table/{season.id}")

        assert response.status_code == 200
        data = response.json()
        assert "league" in data
        assert "season" in data
        assert "table" in data
        assert data["league"]["id"] == comp.id
        assert data["season"]["id"] == season.id
        assert len(data["table"]) == 2

    def test_returns_empty_table_when_no_teams(self, client: TestClient, db_session) -> None:
        """Test that empty table is returned when season has no teams."""
        nation, comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_empty_list_response(client, f"/api/v1/leagues/{comp.id}/table/{season.id}", "table")

    def test_handles_various_invalid_league_id_types_for_table(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid league_id types return validation error for table endpoint."""
        nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, f"/api/v1/leagues/{{invalid_id}}/table/{season.id}"
        )

    def test_handles_various_invalid_season_id_types_for_table(
        self, client: TestClient, db_session
    ) -> None:
        """Test that various invalid season_id types return validation error for table endpoint."""
        nation, comp, _season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_invalid_id_types_return_422(
            client, f"/api/v1/leagues/{comp.id}/table/{{invalid_id}}"
        )

    def test_table_entries_sorted_by_position(self, client: TestClient, db_session) -> None:
        """Test that table entries are sorted by position."""
        nation, comp, season = create_basic_season_setup(db_session)
        team1 = TeamFactory(nation=nation)
        team2 = TeamFactory(nation=nation)
        team3 = TeamFactory(nation=nation)

        TeamStatsFactory(team=team1, season=season, ranking=3)
        TeamStatsFactory(team=team2, season=season, ranking=1)
        TeamStatsFactory(team=team3, season=season, ranking=2)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/table/{season.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["table"]) == 3
        positions = [entry["position"] for entry in data["table"]]
        assert positions == sorted(positions)
