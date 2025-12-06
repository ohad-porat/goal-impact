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
    assert_422_validation_error,
    assert_empty_list_response,
    create_basic_season_setup,
)


class TestGetLeaguesRoute:
    """Tests for GET /api/v1/leagues/ endpoint."""

    def test_returns_empty_list_when_no_leagues(self, client: TestClient, db_session):
        """Test that empty list is returned when no leagues exist."""
        assert_empty_list_response(client, "/api/v1/leagues/", "leagues")

    def test_returns_all_leagues_successfully(self, client: TestClient, db_session):
        """Test that all leagues are returned with correct structure."""
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")

        comp1 = CompetitionFactory(name="Premier League", nation=nation1, tier="1st")
        comp2 = CompetitionFactory(name="La Liga", nation=nation2, tier="1st")

        SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get("/api/v1/leagues/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["leagues"]) >= 2
        league_names = [league_item["name"] for league_item in data["leagues"]]
        assert "Premier League" in league_names
        assert "La Liga" in league_names

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        nation = NationFactory(name="England", country_code="ENG")
        comp = CompetitionFactory(name="Premier League", nation=nation, tier="1st")
        SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get("/api/v1/leagues/")

        assert response.status_code == 200
        data = response.json()
        assert "leagues" in data
        assert isinstance(data["leagues"], list)

        if len(data["leagues"]) > 0:
            league = next(
                (league_item for league_item in data["leagues"] if league_item["id"] == comp.id),
                None,
            )
            if league:
                assert "id" in league
                assert "name" in league
                assert "country" in league
                assert "gender" in league
                assert "tier" in league
                assert "available_seasons" in league
                assert isinstance(league["id"], int)
                assert isinstance(league["name"], str)
                assert isinstance(league["country"], str)

    def test_includes_season_range(self, client: TestClient, db_session):
        """Test that available_seasons is included in response."""
        nation = NationFactory(name="England", country_code="ENG")
        comp = CompetitionFactory(name="Premier League", nation=nation)
        SeasonFactory(competition=comp, start_year=2022, end_year=2023)
        SeasonFactory(competition=comp, start_year=2023, end_year=2024)
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

    def test_returns_empty_list_when_no_seasons(self, client: TestClient, db_session):
        """Test that empty list is returned when no seasons exist."""
        assert_empty_list_response(client, "/api/v1/leagues/seasons", "seasons")

    def test_returns_all_seasons_successfully(self, client: TestClient, db_session):
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

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        nation, comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        response = client.get("/api/v1/leagues/seasons")

        assert response.status_code == 200
        data = response.json()
        assert "seasons" in data
        assert isinstance(data["seasons"], list)

        if len(data["seasons"]) > 0:
            season_data = next((s for s in data["seasons"] if s["id"] == season.id), None)
            if season_data:
                assert "id" in season_data
                assert "start_year" in season_data
                assert "end_year" in season_data
                assert "display_name" in season_data
                assert isinstance(season_data["id"], int)
                assert isinstance(season_data["start_year"], int)

    def test_sorts_by_start_year_descending(self, client: TestClient, db_session):
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

    def test_returns_404_when_league_not_found(self, client: TestClient, db_session):
        """Test that 404 is returned when league doesn't exist."""
        assert_404_not_found(client, "/api/v1/leagues/99999/seasons")

    def test_returns_seasons_for_league_successfully(self, client: TestClient, db_session):
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

    def test_returns_empty_list_when_no_seasons(self, client: TestClient, db_session):
        """Test that empty list is returned when league has no seasons."""
        nation = NationFactory()
        comp = CompetitionFactory(nation=nation)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/seasons")
        assert response.status_code == 200
        data = response.json()
        assert data["seasons"] == []

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        _nation, comp, _season = create_basic_season_setup(db_session)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/seasons")

        assert response.status_code == 200
        data = response.json()
        assert "seasons" in data
        assert isinstance(data["seasons"], list)

        if len(data["seasons"]) > 0:
            season_data = data["seasons"][0]
            assert "id" in season_data
            assert "start_year" in season_data
            assert "end_year" in season_data
            assert "display_name" in season_data

    def test_handles_invalid_league_id_type(self, client: TestClient, db_session):
        """Test that invalid league_id type returns validation error."""
        assert_422_validation_error(client, "/api/v1/leagues/not-a-number/seasons")

    def test_only_returns_seasons_for_specified_league(self, client: TestClient, db_session):
        """Test that only seasons for the specified league are returned."""
        nation1 = NationFactory()
        nation2 = NationFactory()
        comp1 = CompetitionFactory(nation=nation1)
        comp2 = CompetitionFactory(nation=nation2)

        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp1.id}/seasons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["seasons"]) == 1
        assert data["seasons"][0]["id"] == season1.id


class TestGetLeagueTableRoute:
    """Tests for GET /api/v1/leagues/{league_id}/table/{season_id} endpoint."""

    def test_returns_404_when_league_not_found(self, client: TestClient, db_session):
        """Test that 404 is returned when league doesn't exist."""
        _nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/leagues/99999/table/{season.id}", "league")

    def test_returns_404_when_season_not_found(self, client: TestClient, db_session):
        """Test that 404 is returned when season doesn't exist for league."""
        _nation, comp, _season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_404_not_found(client, f"/api/v1/leagues/{comp.id}/table/99999", "season")

    def test_returns_league_table_successfully(self, client: TestClient, db_session):
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

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        TeamStatsFactory(team=team, season=season, ranking=1)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/table/{season.id}")

        assert response.status_code == 200
        data = response.json()

        assert "id" in data["league"]
        assert "name" in data["league"]
        assert "country" in data["league"]
        assert isinstance(data["league"]["id"], int)

        assert "id" in data["season"]
        assert "start_year" in data["season"]
        assert "display_name" in data["season"]
        assert isinstance(data["season"]["id"], int)

        assert isinstance(data["table"], list)
        if len(data["table"]) > 0:
            entry = data["table"][0]
            assert "position" in entry
            assert "team_id" in entry
            assert "team_name" in entry
            assert "matches_played" in entry
            assert "wins" in entry
            assert "draws" in entry
            assert "losses" in entry
            assert "goals_for" in entry
            assert "goals_against" in entry
            assert "goal_difference" in entry
            assert "points" in entry

    def test_returns_empty_table_when_no_teams(self, client: TestClient, db_session):
        """Test that empty table is returned when season has no teams."""
        nation, comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        response = client.get(f"/api/v1/leagues/{comp.id}/table/{season.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["table"] == []

    def test_handles_invalid_league_id_type(self, client: TestClient, db_session):
        """Test that invalid league_id type returns validation error."""
        nation, _comp, season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_422_validation_error(client, f"/api/v1/leagues/not-a-number/table/{season.id}")

    def test_handles_invalid_season_id_type(self, client: TestClient, db_session):
        """Test that invalid season_id type returns validation error."""
        nation, comp, _season = create_basic_season_setup(db_session)
        db_session.commit()

        assert_422_validation_error(client, f"/api/v1/leagues/{comp.id}/table/not-a-number")

    def test_table_entries_sorted_by_position(self, client: TestClient, db_session):
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
