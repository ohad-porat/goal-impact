"""Unit tests for search service layer."""

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
