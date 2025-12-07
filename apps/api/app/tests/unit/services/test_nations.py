"""Unit tests for nations service layer."""

from app.services.nations import (
    get_all_nations_with_player_count,
    get_competitions_for_nation,
    get_top_players_for_nation,
    tier_order,
)
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    TeamFactory,
)
from app.tests.utils.helpers import create_basic_season_setup


class TestTierOrder:
    """Tests for tier_order function."""

    def test_returns_1_for_first_tier(self) -> None:
        """Test that '1st' tier returns 1."""
        assert tier_order("1st") == 1

    def test_returns_2_for_second_tier(self) -> None:
        """Test that '2nd' tier returns 2."""
        assert tier_order("2nd") == 2

    def test_returns_3_for_third_tier(self) -> None:
        """Test that '3rd' tier returns 3."""
        assert tier_order("3rd") == 3

    def test_returns_50_for_unknown_tier(self) -> None:
        """Test that unknown tier returns 50."""
        assert tier_order("4th") == 50
        assert tier_order("Unknown") == 50

    def test_returns_99_for_none(self) -> None:
        """Test that None tier returns 99."""
        assert tier_order(None) == 99


class TestGetCompetitionsForNation:
    """Tests for get_competitions_for_nation function."""

    def test_returns_competitions_for_nation(self, db_session) -> None:
        """Test that competitions are returned for a nation."""
        nation = NationFactory()
        CompetitionFactory(name="Premier League", nation=nation, tier="1st")
        CompetitionFactory(name="Championship", nation=nation, tier="2nd")

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert len(result) == 2
        assert any(c.name == "Premier League" for c in result)
        assert any(c.name == "Championship" for c in result)

    def test_includes_season_count(self, db_session) -> None:
        """Test that season_count is included in results."""
        nation, comp, _ = create_basic_season_setup(db_session)
        SeasonFactory(competition=comp, start_year=2022, end_year=2023)

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert len(result) == 1
        assert result[0].season_count == 2

    def test_sets_has_seasons_true_when_seasons_exist(self, db_session) -> None:
        """Test that has_seasons is True when seasons exist."""
        nation, comp, _ = create_basic_season_setup(db_session)

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert len(result) == 1
        assert result[0].has_seasons is True

    def test_sets_has_seasons_false_when_no_seasons(self, db_session) -> None:
        """Test that has_seasons is False when no seasons exist."""
        nation = NationFactory()
        CompetitionFactory(nation=nation)

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert len(result) == 1
        assert result[0].has_seasons is False
        assert result[0].season_count == 0

    def test_sorts_by_tier_then_name(self, db_session) -> None:
        """Test that competitions are sorted by tier then name."""
        nation = NationFactory()
        CompetitionFactory(name="Championship", nation=nation, tier="2nd")
        CompetitionFactory(name="Premier League", nation=nation, tier="1st")
        CompetitionFactory(name="League One", nation=nation, tier="3rd")

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert len(result) == 3
        assert result[0].name == "Premier League"
        assert result[0].tier == "1st"
        assert result[1].name == "Championship"
        assert result[1].tier == "2nd"
        assert result[2].name == "League One"
        assert result[2].tier == "3rd"

    def test_handles_competitions_without_tier(self, db_session) -> None:
        """Test that competitions without tier are sorted last."""
        nation = NationFactory()
        CompetitionFactory(name="Premier League", nation=nation, tier="1st")
        CompetitionFactory(name="Unknown League", nation=nation, tier=None)

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert len(result) == 2
        assert result[0].name == "Premier League"
        assert result[1].name == "Unknown League"
        assert result[1].tier is None

    def test_returns_empty_list_when_no_competitions(self, db_session) -> None:
        """Test that empty list is returned when nation has no competitions."""
        nation = NationFactory()

        db_session.commit()

        result = get_competitions_for_nation(db_session, nation.id)

        assert result == []


class TestGetAllNationsWithPlayerCount:
    """Tests for get_all_nations_with_player_count function."""

    def test_returns_all_nations_with_player_count(self, db_session) -> None:
        """Test that all nations are returned with player counts."""
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")

        PlayerFactory(nation=nation1)
        PlayerFactory(nation=nation1)
        PlayerFactory(nation=nation2)

        db_session.commit()

        result = get_all_nations_with_player_count(db_session)

        assert len(result) >= 2
        england = next((n for n in result if n.name == "England"), None)
        spain = next((n for n in result if n.name == "Spain"), None)
        assert england is not None
        assert england.player_count == 2
        assert spain is not None
        assert spain.player_count == 1

    def test_sets_player_count_to_zero_when_no_players(self, db_session) -> None:
        """Test that player_count is 0 when nation has no players."""
        NationFactory(name="New Nation", country_code="NEW")

        db_session.commit()

        result = get_all_nations_with_player_count(db_session)

        new_nation = next((n for n in result if n.name == "New Nation"), None)
        assert new_nation is not None
        assert new_nation.player_count == 0

    def test_sorts_by_name(self, db_session) -> None:
        """Test that nations are sorted by name."""
        NationFactory(name="Zimbabwe", country_code="ZWE")
        NationFactory(name="Argentina", country_code="ARG")
        NationFactory(name="Brazil", country_code="BRA")

        db_session.commit()

        result = get_all_nations_with_player_count(db_session)

        arg = next((n for n in result if n.name == "Argentina"), None)
        bra = next((n for n in result if n.name == "Brazil"), None)
        zwe = next((n for n in result if n.name == "Zimbabwe"), None)

        assert arg is not None
        assert bra is not None
        assert zwe is not None

        arg_idx = result.index(arg)
        bra_idx = result.index(bra)
        zwe_idx = result.index(zwe)

        assert arg_idx < bra_idx < zwe_idx

    def test_includes_governing_body(self, db_session) -> None:
        """Test that governing_body is included in results."""
        NationFactory(name="England", country_code="ENG", governing_body="UEFA")

        db_session.commit()

        result = get_all_nations_with_player_count(db_session)

        england = next((n for n in result if n.name == "England"), None)
        assert england is not None
        assert england.governing_body == "UEFA"

    def test_sets_governing_body_to_na_when_none(self, db_session) -> None:
        """Test that governing_body is 'N/A' when None."""
        NationFactory(name="New Nation", country_code="NEW", governing_body=None)

        db_session.commit()

        result = get_all_nations_with_player_count(db_session)

        new_nation = next((n for n in result if n.name == "New Nation"), None)
        assert new_nation is not None
        assert new_nation.governing_body == "N/A"


class TestGetTopPlayersForNation:
    """Tests for get_top_players_for_nation function."""

    def test_returns_top_players_by_goal_value(self, db_session) -> None:
        """Test that top players are returned sorted by goal value."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)
        player3 = PlayerFactory(name="Player 3", nation=nation)

        PlayerStatsFactory(player=player1, season=season, team=team, goal_value=50.5)
        PlayerStatsFactory(player=player2, season=season, team=team, goal_value=30.2)
        PlayerStatsFactory(player=player3, season=season, team=team, goal_value=75.8)

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=10)

        assert len(result) == 3
        assert result[0].name == "Player 3"
        assert result[0].total_goal_value == 75.8
        assert result[1].name == "Player 1"
        assert result[1].total_goal_value == 50.5
        assert result[2].name == "Player 2"
        assert result[2].total_goal_value == 30.2

    def test_respects_limit_parameter(self, db_session) -> None:
        """Test that limit parameter is respected."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(player=player, season=season, team=team, goal_value=float(i))

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=5)

        assert len(result) == 5

    def test_sums_goal_value_across_multiple_seasons(self, db_session) -> None:
        """Test that goal values are summed across multiple seasons."""
        nation, comp, season1 = create_basic_season_setup(db_session)
        season2 = SeasonFactory(competition=comp, start_year=2024, end_year=2025)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(name="Top Player", nation=nation)
        PlayerStatsFactory(player=player, season=season1, team=team, goal_value=25.5)
        PlayerStatsFactory(player=player, season=season2, team=team, goal_value=30.2)

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 55.7

    def test_returns_zero_goal_value_when_none(self, db_session) -> None:
        """Test that zero is returned when player has no goal value."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(player=player, season=season, team=team, goal_value=None)

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 0.0

    def test_sorts_by_name_when_goal_value_tied(self, db_session) -> None:
        """Test that players are sorted by name when goal value is tied."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Alice", nation=nation)
        player2 = PlayerFactory(name="Bob", nation=nation)
        player3 = PlayerFactory(name="Charlie", nation=nation)

        PlayerStatsFactory(player=player1, season=season, team=team, goal_value=50.0)
        PlayerStatsFactory(player=player2, season=season, team=team, goal_value=50.0)
        PlayerStatsFactory(player=player3, season=season, team=team, goal_value=50.0)

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=10)

        assert len(result) == 3
        assert result[0].name == "Alice"
        assert result[1].name == "Bob"
        assert result[2].name == "Charlie"

    def test_only_returns_players_for_specified_nation(self, db_session) -> None:
        """Test that only players for the specified nation are returned."""
        nation1, comp1, season1 = create_basic_season_setup(
            db_session, nation=None, comp_name="League 1"
        )
        nation2 = NationFactory(name="Spain", country_code="ESP")
        comp2 = CompetitionFactory(nation=nation2)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)

        team1 = TeamFactory(nation=nation1)
        team2 = TeamFactory(nation=nation2)

        player1 = PlayerFactory(nation=nation1)
        player2 = PlayerFactory(nation=nation2)

        PlayerStatsFactory(player=player1, season=season1, team=team1, goal_value=50.0)
        PlayerStatsFactory(player=player2, season=season2, team=team2, goal_value=75.0)

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation1.id, limit=10)

        assert len(result) == 1
        assert result[0].name == player1.name

    def test_returns_empty_list_when_no_players(self, db_session) -> None:
        """Test that empty list is returned when nation has no players."""
        nation = NationFactory()

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=10)

        assert result == []

    def test_only_includes_players_with_stats(self, db_session) -> None:
        """Test that only players with stats are included."""
        nation = NationFactory()
        PlayerFactory(nation=nation)
        PlayerFactory(nation=nation)

        db_session.commit()

        result = get_top_players_for_nation(db_session, nation.id, limit=10)

        assert result == []
