"""Unit tests for search service layer."""

import pytest

from app.services.search import search_all
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    TeamFactory,
)
from app.tests.utils.helpers import create_basic_season_setup


class TestSearchAll:
    """Tests for search_all function."""

    def test_returns_empty_list_when_query_is_empty(self, db_session) -> None:
        """Test that empty list is returned when query is empty."""
        result = search_all(db_session, "")

        assert result == []

    def test_returns_empty_list_when_query_is_whitespace(self, db_session) -> None:
        """Test that empty list is returned when query is whitespace."""
        result = search_all(db_session, "   ")

        assert result == []

    def test_finds_players_by_prefix(self, db_session) -> None:
        """Test that players are found by prefix match."""
        nation = NationFactory()
        player1 = PlayerFactory(name="Alice Smith", nation=nation)
        PlayerFactory(name="Bob Johnson", nation=nation)
        PlayerFactory(name="Charlie Brown", nation=nation)

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Alice Smith"
        assert result[0].type == "Player"
        assert result[0].id == player1.id

    def test_finds_players_by_contains(self, db_session) -> None:
        """Test that players are found by contains match."""
        nation = NationFactory()
        PlayerFactory(name="Alice Smith", nation=nation)
        PlayerFactory(name="Bob Johnson", nation=nation)

        db_session.commit()

        result = search_all(db_session, "smith", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Alice Smith"
        assert result[0].type == "Player"

    def test_finds_clubs_by_prefix(self, db_session) -> None:
        """Test that clubs are found by prefix match."""
        nation = NationFactory()
        team1 = TeamFactory(name="Arsenal FC", nation=nation)
        TeamFactory(name="Chelsea FC", nation=nation)

        db_session.commit()

        result = search_all(db_session, "arsenal", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Arsenal FC"
        assert result[0].type == "Club"
        assert result[0].id == team1.id

    def test_finds_clubs_by_contains(self, db_session) -> None:
        """Test that clubs are found by contains match."""
        nation = NationFactory()
        TeamFactory(name="Manchester United", nation=nation)
        TeamFactory(name="Manchester City", nation=nation)

        db_session.commit()

        result = search_all(db_session, "united", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Manchester United"
        assert result[0].type == "Club"

    def test_finds_competitions_by_prefix(self, db_session) -> None:
        """Test that competitions are found by prefix match."""
        nation = NationFactory()
        comp1 = CompetitionFactory(name="Premier League", nation=nation)
        CompetitionFactory(name="Championship", nation=nation)

        db_session.commit()

        result = search_all(db_session, "premier", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Premier League"
        assert result[0].type == "Competition"
        assert result[0].id == comp1.id

    def test_finds_competitions_by_contains(self, db_session) -> None:
        """Test that competitions are found by contains match."""
        nation = NationFactory()
        CompetitionFactory(name="Premier League", nation=nation)

        db_session.commit()

        result = search_all(db_session, "league", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Premier League"
        assert result[0].type == "Competition"

    def test_finds_nations_by_prefix(self, db_session) -> None:
        """Test that nations are found by prefix match."""
        nation1 = NationFactory(name="England", country_code="ENG")
        NationFactory(name="Spain", country_code="ESP")

        db_session.commit()

        result = search_all(db_session, "england", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "England"
        assert result[0].type == "Nation"
        assert result[0].id == nation1.id

    def test_finds_nations_by_contains(self, db_session) -> None:
        """Test that nations are found by contains match."""
        NationFactory(name="United States", country_code="USA")

        db_session.commit()

        result = search_all(db_session, "states", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "United States"
        assert result[0].type == "Nation"

    def test_is_case_insensitive(self, db_session) -> None:
        """Test that search is case insensitive."""
        nation = NationFactory()
        PlayerFactory(name="Alice Smith", nation=nation)

        db_session.commit()

        result = search_all(db_session, "ALICE", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Alice Smith"

    def test_prefers_prefix_over_contains(self, db_session) -> None:
        """Test that prefix matches come before contains matches."""
        nation = NationFactory()
        PlayerFactory(name="Alice Smith", nation=nation)
        PlayerFactory(name="Bob Alice", nation=nation)

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=5)

        assert len(result) == 2
        assert result[0].name == "Alice Smith"
        assert result[1].name == "Bob Alice"

    def test_limits_each_type_independently(self, db_session) -> None:
        """Test that each type is limited independently."""
        nation = NationFactory()

        PlayerFactory(name="Alice Smith", nation=nation)
        PlayerFactory(name="Alice Jones", nation=nation)
        TeamFactory(name="Arsenal FC", nation=nation)
        TeamFactory(name="Arsenal United", nation=nation)
        CompetitionFactory(name="Premier League", nation=nation)
        CompetitionFactory(name="Premier Championship", nation=nation)
        NationFactory(name="England")
        NationFactory(name="English")

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=1)

        player_count = sum(1 for r in result if r.type == "Player")
        club_count = sum(1 for r in result if r.type == "Club")
        comp_count = sum(1 for r in result if r.type == "Competition")
        nation_count = sum(1 for r in result if r.type == "Nation")

        assert player_count == 1
        assert club_count == 0
        assert comp_count == 0
        assert nation_count == 0

    def test_sorts_players_by_matches_played_in_prefix(self, db_session) -> None:
        """Test that players are sorted by matches_played in prefix results."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Alice Smith", nation=nation)
        player2 = PlayerFactory(name="Alice Jones", nation=nation)
        player3 = PlayerFactory(name="Alice Brown", nation=nation)

        PlayerStatsFactory(player=player1, season=season, team=team, matches_played=10)
        PlayerStatsFactory(player=player2, season=season, team=team, matches_played=30)
        PlayerStatsFactory(player=player3, season=season, team=team, matches_played=20)

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=5)

        assert len(result) >= 3
        alice_results = [r for r in result if r.name.startswith("Alice")]
        assert alice_results[0].name == "Alice Jones"
        assert alice_results[1].name == "Alice Brown"
        assert alice_results[2].name == "Alice Smith"

    def test_handles_players_without_stats(self, db_session) -> None:
        """Test that players without stats are handled correctly."""
        nation = NationFactory()
        PlayerFactory(name="Alice Smith", nation=nation)

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Alice Smith"

    def test_returns_multiple_types(self, db_session) -> None:
        """Test that multiple types can be returned in one search."""
        nation = NationFactory(name="England", country_code="ENG")
        PlayerFactory(name="Alice Smith", nation=nation)
        TeamFactory(name="Arsenal FC", nation=nation)
        CompetitionFactory(name="Premier League", nation=nation)

        db_session.commit()

        result = search_all(db_session, "a", limit_per_type=5)

        types = {r.type for r in result}
        assert len(types) >= 2

    def test_handles_stripped_query(self, db_session) -> None:
        """Test that query is stripped of whitespace."""
        nation = NationFactory()
        PlayerFactory(name="Alice Smith", nation=nation)

        db_session.commit()

        result = search_all(db_session, "  alice  ", limit_per_type=5)

        assert len(result) == 1
        assert result[0].name == "Alice Smith"

    @pytest.mark.parametrize("type_filter", ["Player", "Club", "Competition", "Nation"])
    def test_type_filter_returns_only_matching_type(self, db_session, type_filter) -> None:
        """Test that type_filter returns only entities of the specified type."""
        nation = NationFactory(name="Test Nation", country_code="TST")
        player = PlayerFactory(name="Test Player", nation=nation)
        team = TeamFactory(name="Test Club", nation=nation)
        competition = CompetitionFactory(name="Test Competition", nation=nation)

        db_session.commit()

        result = search_all(db_session, "test", limit_per_type=5, type_filter=type_filter)

        assert len(result) == 1
        assert all(r.type == type_filter for r in result)

        expected_map = {
            "Player": (player.id, "Test Player"),
            "Club": (team.id, "Test Club"),
            "Competition": (competition.id, "Test Competition"),
            "Nation": (nation.id, "Test Nation"),
        }
        expected_id, expected_name = expected_map[type_filter]
        assert result[0].id == expected_id
        assert result[0].name == expected_name

    def test_type_filter_none_returns_all_types(self, db_session) -> None:
        """Test that type_filter=None returns all types (backward compatibility)."""
        nation = NationFactory(name="Test Nation", country_code="TST")
        PlayerFactory(name="Test Player", nation=nation)
        TeamFactory(name="Test Club", nation=nation)
        CompetitionFactory(name="Test Competition", nation=nation)

        db_session.commit()

        result = search_all(db_session, "test", limit_per_type=5, type_filter=None)

        types = {r.type for r in result}
        assert types == {"Player", "Club", "Competition", "Nation"}
        assert len(result) == 4

    def test_type_filter_invalid_value_returns_empty(self, db_session) -> None:
        """Test that invalid type_filter value returns empty results."""
        nation = NationFactory()
        PlayerFactory(name="Test Player", nation=nation)
        TeamFactory(name="Test Club", nation=nation)

        db_session.commit()

        result = search_all(db_session, "test", limit_per_type=5, type_filter="InvalidType")

        assert result == []

    def test_type_filter_works_with_prefix_matches(self, db_session) -> None:
        """Test that type_filter works with prefix matches."""
        nation = NationFactory()
        player1 = PlayerFactory(name="Alice Smith", nation=nation)
        PlayerFactory(name="Bob Alice", nation=nation)
        TeamFactory(name="Alice FC", nation=nation)

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=5, type_filter="Player")

        assert len(result) == 2
        assert all(r.type == "Player" for r in result)
        assert result[0].id == player1.id
        assert result[0].name == "Alice Smith"

    def test_type_filter_works_with_contains_matches(self, db_session) -> None:
        """Test that type_filter works with contains matches."""
        nation = NationFactory()
        PlayerFactory(name="Alice Smith", nation=nation)
        player2 = PlayerFactory(name="Bob Alice", nation=nation)
        TeamFactory(name="Team Alice", nation=nation)

        db_session.commit()

        result = search_all(db_session, "alice", limit_per_type=5, type_filter="Player")

        assert len(result) == 2
        assert all(r.type == "Player" for r in result)
        player_ids = {r.id for r in result}
        assert player2.id in player_ids

    def test_type_filter_respects_limit_per_type(self, db_session) -> None:
        """Test that type_filter respects limit_per_type for the filtered type."""
        nation = NationFactory()

        for i in range(10):
            PlayerFactory(name=f"Test Player {i}", nation=nation)

        db_session.commit()

        result = search_all(db_session, "test", limit_per_type=3, type_filter="Player")

        assert len(result) == 3
        assert all(r.type == "Player" for r in result)

    def test_type_filter_with_multiple_matches(self, db_session) -> None:
        """Test that type_filter works correctly when multiple entities of that type match."""
        nation = NationFactory()
        player1 = PlayerFactory(name="Test Player One", nation=nation)
        player2 = PlayerFactory(name="Test Player Two", nation=nation)
        TeamFactory(name="Test Club", nation=nation)
        CompetitionFactory(name="Test Competition", nation=nation)

        db_session.commit()

        result = search_all(db_session, "test", limit_per_type=5, type_filter="Player")

        assert len(result) == 2
        assert all(r.type == "Player" for r in result)
        player_ids = {r.id for r in result}
        assert player1.id in player_ids
        assert player2.id in player_ids

    def test_type_filter_case_insensitive_search(self, db_session) -> None:
        """Test that search is case-insensitive with type_filter."""
        nation = NationFactory()
        player = PlayerFactory(name="John Smith", nation=nation)

        db_session.commit()

        result_lower = search_all(db_session, "john", limit_per_type=5, type_filter="Player")
        result_upper = search_all(db_session, "JOHN", limit_per_type=5, type_filter="Player")
        result_mixed = search_all(db_session, "JoHn", limit_per_type=5, type_filter="Player")

        assert len(result_lower) == 1
        assert len(result_upper) == 1
        assert len(result_mixed) == 1

        assert result_lower[0].id == player.id
        assert result_upper[0].id == player.id
        assert result_mixed[0].id == player.id

    def test_type_filter_with_empty_query_returns_empty(self, db_session) -> None:
        """Test that empty query returns empty results even with type_filter."""
        nation = NationFactory()
        PlayerFactory(name="Test Player", nation=nation)

        db_session.commit()

        result_empty = search_all(db_session, "", limit_per_type=5, type_filter="Player")
        assert result_empty == []

        result_whitespace = search_all(db_session, "   ", limit_per_type=5, type_filter="Player")
        assert result_whitespace == []
