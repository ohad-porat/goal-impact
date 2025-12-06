"""Integration tests for nations router endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.tests.utils.helpers import (
    assert_404_not_found,
    assert_422_validation_error,
    assert_empty_list_response,
    create_basic_season_setup,
)


class TestGetNationsRoute:
    """Tests for GET /api/v1/nations/ endpoint."""

    def test_returns_empty_list_when_no_nations(self, client: TestClient, db_session):
        """Test that empty list is returned when no nations exist."""
        assert_empty_list_response(client, "/api/v1/nations/", "nations")

    def test_returns_all_nations_successfully(self, client: TestClient, db_session):
        """Test that all nations are returned with correct structure."""
        nation1 = NationFactory(name="England", country_code="ENG", governing_body="UEFA")
        nation2 = NationFactory(name="Spain", country_code="ESP", governing_body="UEFA")
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["nations"]) >= 2
        nations_dict = {n["name"]: n for n in data["nations"]}
        assert "England" in nations_dict
        assert "Spain" in nations_dict

    def test_includes_player_count(self, client: TestClient, db_session):
        """Test that player_count is included in response."""
        nation = NationFactory()
        PlayerFactory(nation=nation)
        PlayerFactory(nation=nation)
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        nation_data = next((n for n in data["nations"] if n["id"] == nation.id), None)
        assert nation_data is not None
        assert nation_data["player_count"] == 2

    def test_sets_player_count_to_zero_when_no_players(self, client: TestClient, db_session):
        """Test that player_count is 0 when nation has no players."""
        _nation = NationFactory(name="New Nation", country_code="NEW")
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        nation_data = next((n for n in data["nations"] if n["name"] == "New Nation"), None)
        assert nation_data is not None
        assert nation_data["player_count"] == 0

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        nation = NationFactory(name="Test Nation", country_code="TST", governing_body="UEFA")
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        assert "nations" in data
        assert isinstance(data["nations"], list)

        if len(data["nations"]) > 0:
            nation_data = next((n for n in data["nations"] if n["id"] == nation.id), None)
            if nation_data:
                assert "id" in nation_data
                assert "name" in nation_data
                assert "country_code" in nation_data
                assert "governing_body" in nation_data
                assert "player_count" in nation_data
                assert isinstance(nation_data["id"], int)
                assert isinstance(nation_data["name"], str)
                assert isinstance(nation_data["player_count"], int)

    def test_includes_governing_body(self, client: TestClient, db_session):
        """Test that governing_body is included in response."""
        nation = NationFactory(name="England", country_code="ENG", governing_body="UEFA")
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        nation_data = next((n for n in data["nations"] if n["id"] == nation.id), None)
        assert nation_data is not None
        assert nation_data["governing_body"] == "UEFA"

    def test_sets_governing_body_to_na_when_none(self, client: TestClient, db_session):
        """Test that governing_body is 'N/A' when None."""
        nation = NationFactory(name="New Nation", country_code="NEW", governing_body=None)
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        nation_data = next((n for n in data["nations"] if n["id"] == nation.id), None)
        assert nation_data is not None
        assert nation_data["governing_body"] == "N/A"

    def test_sorts_nations_by_name(self, client: TestClient, db_session):
        """Test that nations are sorted by name."""
        NationFactory(name="Zimbabwe", country_code="ZWE")
        NationFactory(name="Argentina", country_code="ARG")
        NationFactory(name="Brazil", country_code="BRA")
        db_session.commit()

        response = client.get("/api/v1/nations/")

        assert response.status_code == 200
        data = response.json()
        names = [n["name"] for n in data["nations"]]
        arg_idx = names.index("Argentina")
        bra_idx = names.index("Brazil")
        zwe_idx = names.index("Zimbabwe")
        assert arg_idx < bra_idx < zwe_idx


class TestGetNationDetailsRoute:
    """Tests for GET /api/v1/nations/{nation_id} endpoint."""

    def test_returns_404_when_nation_not_found(self, client: TestClient, db_session):
        """Test that 404 is returned when nation doesn't exist."""
        assert_404_not_found(client, "/api/v1/nations/99999")

    def test_returns_nation_details_successfully(self, client: TestClient, db_session):
        """Test that nation details are returned with correct structure."""
        nation = NationFactory(name="England", country_code="ENG", governing_body="UEFA")
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert "nation" in data
        assert "competitions" in data
        assert "clubs" in data
        assert "players" in data
        assert data["nation"]["id"] == nation.id
        assert data["nation"]["name"] == "England"
        assert data["nation"]["country_code"] == "ENG"
        assert isinstance(data["competitions"], list)
        assert isinstance(data["clubs"], list)
        assert isinstance(data["players"], list)

    def test_includes_competitions(self, client: TestClient, db_session):
        """Test that competitions are included in response."""
        nation = NationFactory()
        _comp1 = CompetitionFactory(name="Premier League", nation=nation, tier="1st")
        _comp2 = CompetitionFactory(name="Championship", nation=nation, tier="2nd")
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["competitions"]) == 2
        comp_names = [c["name"] for c in data["competitions"]]
        assert "Premier League" in comp_names
        assert "Championship" in comp_names

    def test_includes_clubs(self, client: TestClient, db_session):
        """Test that clubs are included in response."""
        nation, _comp, season = create_basic_season_setup(db_session)
        team1 = TeamFactory(name="Arsenal FC", nation=nation)
        team2 = TeamFactory(name="Chelsea FC", nation=nation)
        TeamStatsFactory(team=team1, season=season, ranking=1)
        TeamStatsFactory(team=team2, season=season, ranking=2)
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["clubs"]) >= 2
        club_names = [c["name"] for c in data["clubs"]]
        assert "Arsenal FC" in club_names or "Chelsea FC" in club_names

    def test_includes_players(self, client: TestClient, db_session):
        """Test that players are included in response."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)

        PlayerStatsFactory(player=player1, season=season, team=team, goal_value=50.5)
        PlayerStatsFactory(player=player2, season=season, team=team, goal_value=30.2)
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) >= 2
        player_names = [p["name"] for p in data["players"]]
        assert "Player 1" in player_names or "Player 2" in player_names

    def test_returns_empty_lists_when_no_data(self, client: TestClient, db_session):
        """Test that empty lists are returned when nation has no competitions/clubs/players."""
        nation = NationFactory()
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["nation"]["id"] == nation.id
        assert data["competitions"] == []
        assert data["clubs"] == []
        assert data["players"] == []

    def test_response_structure_is_correct(self, client: TestClient, db_session):
        """Test that response structure matches the expected schema."""
        nation = NationFactory(name="Test Nation", country_code="TST", governing_body="UEFA")
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()

        assert "id" in data["nation"]
        assert "name" in data["nation"]
        assert "country_code" in data["nation"]
        assert "governing_body" in data["nation"]
        assert isinstance(data["nation"]["id"], int)
        assert isinstance(data["nation"]["name"], str)

        assert isinstance(data["competitions"], list)
        if len(data["competitions"]) > 0:
            comp = data["competitions"][0]
            assert "id" in comp
            assert "name" in comp
            assert "tier" in comp
            assert "season_count" in comp
            assert "has_seasons" in comp

        assert isinstance(data["clubs"], list)
        if len(data["clubs"]) > 0:
            club = data["clubs"][0]
            assert "id" in club
            assert "name" in club
            assert "avg_position" in club

        assert isinstance(data["players"], list)
        if len(data["players"]) > 0:
            player = data["players"][0]
            assert "id" in player
            assert "name" in player
            assert "total_goal_value" in player

    @pytest.mark.parametrize("invalid_id", ["not-a-number", "abc", "12.5"])
    def test_handles_various_invalid_nation_id_types(self, client: TestClient, db_session, invalid_id):
        """Test that various invalid nation_id types return validation error."""
        assert_422_validation_error(client, f"/api/v1/nations/{invalid_id}")

    def test_handles_negative_and_zero_nation_id(self, client: TestClient, db_session):
        """Test that negative and zero nation_id return 404."""
        response_neg = client.get("/api/v1/nations/-1")
        response_zero = client.get("/api/v1/nations/0")
        assert response_neg.status_code == 404
        assert response_zero.status_code == 404

    def test_governing_body_defaults_to_na(self, client: TestClient, db_session):
        """Test that governing_body defaults to 'N/A' when None."""
        nation = NationFactory(name="Test Nation", country_code="TST", governing_body=None)
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["nation"]["governing_body"] == "N/A"

    def test_limits_clubs_to_top_10(self, client: TestClient, db_session):
        """Test that clubs are limited to top 10."""
        nation = NationFactory()
        for i in range(15):
            TeamFactory(name=f"Team {i}", nation=nation)
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["clubs"]) <= 10

    def test_limits_players_to_top_20(self, client: TestClient, db_session):
        """Test that players are limited to top 20."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)
        for i in range(25):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(player=player, season=season, team=team, goal_value=float(i))
        db_session.commit()

        response = client.get(f"/api/v1/nations/{nation.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) <= 20
