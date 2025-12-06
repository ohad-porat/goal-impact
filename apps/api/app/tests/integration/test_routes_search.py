"""Integration tests for search router endpoints."""

from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    PlayerFactory,
    TeamFactory,
)
from app.tests.utils.helpers import (
    assert_422_validation_error,
    assert_empty_list_response,
)


class TestSearchRoute:
    """Tests for GET /api/v1/search/ endpoint."""

    def test_returns_empty_list_when_no_results(self, client: TestClient, db_session):
        """Test that empty list is returned when no matches exist."""
        assert_empty_list_response(client, "/api/v1/search/?q=nonexistent", "results")

    def test_requires_query_parameter(self, client: TestClient, db_session):
        """Test that query parameter is required."""
        assert_422_validation_error(client, "/api/v1/search/")

    def test_query_parameter_min_length_validation(self, client: TestClient, db_session):
        """Test that query parameter must have min_length=1."""
        assert_422_validation_error(client, "/api/v1/search/?q=")

    def test_finds_players(self, client: TestClient, db_session):
        """Test that players are found and returned correctly."""
        nation = NationFactory()
        player = PlayerFactory(name="Lionel Messi", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=messi")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 1
        result = next((r for r in data["results"] if r["id"] == player.id), None)
        assert result is not None
        assert result["name"] == "Lionel Messi"
        assert result["type"] == "Player"
        assert result["id"] == player.id

    def test_finds_clubs(self, client: TestClient, db_session):
        """Test that clubs are found and returned correctly."""
        nation = NationFactory()
        team = TeamFactory(name="Arsenal FC", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=arsenal")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 1
        result = next((r for r in data["results"] if r["id"] == team.id), None)
        assert result is not None
        assert result["name"] == "Arsenal FC"
        assert result["type"] == "Club"
        assert result["id"] == team.id

    def test_finds_competitions(self, client: TestClient, db_session):
        """Test that competitions are found and returned correctly."""
        nation = NationFactory()
        comp = CompetitionFactory(name="Premier League", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=premier")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 1
        result = next((r for r in data["results"] if r["id"] == comp.id), None)
        assert result is not None
        assert result["name"] == "Premier League"
        assert result["type"] == "Competition"
        assert result["id"] == comp.id

    def test_finds_nations(self, client: TestClient, db_session):
        """Test that nations are found and returned correctly."""
        nation = NationFactory(name="England", country_code="ENG")
        db_session.commit()

        response = client.get("/api/v1/search/?q=england")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 1
        result = next((r for r in data["results"] if r["id"] == nation.id), None)
        assert result is not None
        assert result["name"] == "England"
        assert result["type"] == "Nation"
        assert result["id"] == nation.id

    def test_returns_multiple_types(self, client: TestClient, db_session):
        """Test that multiple entity types can be returned in one search."""
        nation = NationFactory(name="England", country_code="ENG")
        PlayerFactory(name="Alice Smith", nation=nation)
        TeamFactory(name="Arsenal FC", nation=nation)
        CompetitionFactory(name="Premier League", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=a")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 2
        types = {r["type"] for r in data["results"]}
        assert len(types) >= 2

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        nation = NationFactory()
        _player = PlayerFactory(name="Test Player", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=test")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

        if len(data["results"]) > 0:
            result = data["results"][0]
            assert "id" in result
            assert "name" in result
            assert "type" in result
            assert isinstance(result["id"], int)
            assert isinstance(result["name"], str)
            assert isinstance(result["type"], str)
            assert result["type"] in ["Player", "Club", "Competition", "Nation"]

    def test_is_case_insensitive(self, client: TestClient, db_session):
        """Test that search is case insensitive."""
        nation = NationFactory()
        player = PlayerFactory(name="Alice Smith", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=ALICE")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 1
        result = next((r for r in data["results"] if r["id"] == player.id), None)
        assert result is not None
        assert result["name"] == "Alice Smith"

    def test_handles_whitespace_in_query(self, client: TestClient, db_session):
        """Test that whitespace in query is handled correctly."""
        nation = NationFactory()
        _player = PlayerFactory(name="Alice Smith", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=  alice  ")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_limits_results_per_type(self, client: TestClient, db_session):
        """Test that results are limited per type (limit_per_type=5)."""
        nation = NationFactory()

        for i in range(10):
            PlayerFactory(name=f"Alice {i}", nation=nation)

        db_session.commit()

        response = client.get("/api/v1/search/?q=alice")

        assert response.status_code == 200
        data = response.json()
        player_results = [r for r in data["results"] if r["type"] == "Player"]
        assert len(player_results) <= 5

    def test_finds_by_prefix_and_contains(self, client: TestClient, db_session):
        """Test that both prefix and contains matches work."""
        nation = NationFactory()
        player1 = PlayerFactory(name="Alice Smith", nation=nation)
        player2 = PlayerFactory(name="Bob Alice", nation=nation)
        db_session.commit()

        response = client.get("/api/v1/search/?q=alice")

        assert response.status_code == 200
        data = response.json()
        player_results = [r for r in data["results"] if r["type"] == "Player"]
        assert len(player_results) >= 2
        ids = {r["id"] for r in player_results}
        assert player1.id in ids
        assert player2.id in ids
