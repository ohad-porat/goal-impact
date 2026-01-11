"""Unit tests for leaders service layer."""

from app.services.leaders import get_all_seasons, get_by_season, get_career_totals
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    TeamFactory,
)
from app.tests.utils.helpers import create_basic_season_setup


class TestGetCareerTotals:
    """Tests for get_career_totals function."""

    def test_returns_top_players_sorted_by_goal_value(self, db_session) -> None:
        """Test that players are returned sorted by total goal_value descending."""
        nation = NationFactory(name="England", country_code="ENG")
        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)
        player3 = PlayerFactory(name="Player 3", nation=nation)

        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season,
            team=team,
            goal_value=10.5,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season,
            team=team,
            goal_value=5.2,
            goals_scored=3,
            matches_played=8,
        )
        PlayerStatsFactory(
            player=player3,
            season=season,
            team=team,
            goal_value=15.8,
            goals_scored=7,
            matches_played=12,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 3
        assert result[0].player_name == "Player 3"
        assert result[0].total_goal_value == 15.8
        assert result[1].player_name == "Player 1"
        assert result[1].total_goal_value == 10.5
        assert result[2].player_name == "Player 2"
        assert result[2].total_goal_value == 5.2

    def test_respects_limit_parameter(self, db_session) -> None:
        """Test that limit parameter is respected."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )

        db_session.commit()

        result = get_career_totals(db_session, limit=5)

        assert len(result) == 5

    def test_filters_by_league_id(self, db_session) -> None:
        """Test that league_id parameter filters results correctly."""
        nation = NationFactory()
        comp1 = CompetitionFactory(name="Premier League", nation=nation)
        comp2 = CompetitionFactory(name="Championship", nation=nation)
        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season1,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season2,
            team=team,
            goal_value=8.0,
            goals_scored=4,
            matches_played=8,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10, league_id=comp1.id)

        assert len(result) == 1
        assert result[0].player_name == player1.name
        assert result[0].total_goal_value == 10.0

    def test_excludes_players_with_none_goal_value(self, db_session) -> None:
        """Test that players with None goal_value are excluded."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player_with_value = PlayerFactory(nation=nation)
        player_without_value = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player_with_value,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player_without_value,
            season=season,
            team=team,
            goal_value=None,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].player_name == player_with_value.name

    def test_excludes_players_with_zero_goal_value(self, db_session) -> None:
        """Test that players with zero or negative goal_value are excluded."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player_with_value = PlayerFactory(nation=nation)
        player_with_zero = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player_with_value,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player_with_zero,
            season=season,
            team=team,
            goal_value=0.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].player_name == player_with_value.name

    def test_calculates_goal_value_avg(self, db_session) -> None:
        """Test that goal_value_avg is calculated correctly."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].goal_value_avg == 2.0

    def test_rounds_decimal_values(self, db_session) -> None:
        """Test that decimal values are rounded to two decimals."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=10.123456,
            goals_scored=3,
            matches_played=5,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 10.12
        assert result[0].goal_value_avg == 3.37

    def test_includes_nation_info(self, db_session) -> None:
        """Test that nation info is included when available."""
        nation = NationFactory(name="England", country_code="ENG")
        player = PlayerFactory(name="Test Player", nation=nation)

        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].nation is not None
        assert result[0].nation.name == "England"
        assert result[0].nation.country_code == "ENG"

    def test_handles_players_without_nation(self, db_session) -> None:
        """Test that players without nation are handled correctly."""
        player = PlayerFactory(nation=None)

        _, _, season = create_basic_season_setup(db_session)
        team = TeamFactory()

        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].nation is None

    def test_aggregates_stats_across_multiple_seasons(self, db_session) -> None:
        """Test that stats are aggregated across multiple seasons."""
        nation = NationFactory()
        _, comp, season1 = create_basic_season_setup(
            db_session, nation=nation, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season1,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season2,
            team=team,
            goal_value=7.5,
            goals_scored=3,
            matches_played=6,
        )

        db_session.commit()

        result = get_career_totals(db_session, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 12.5
        assert result[0].total_goals == 5
        assert result[0].total_matches == 11


class TestGetBySeason:
    """Tests for get_by_season function."""

    def test_returns_top_players_for_season(self, db_session) -> None:
        """Test that top players for a season are returned sorted by goal_value."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)
        player3 = PlayerFactory(name="Player 3", nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season,
            team=team,
            goal_value=10.5,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season,
            team=team,
            goal_value=5.2,
            goals_scored=3,
            matches_played=8,
        )
        PlayerStatsFactory(
            player=player3,
            season=season,
            team=team,
            goal_value=15.8,
            goals_scored=7,
            matches_played=12,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 3
        assert result[0].player_name == "Player 3"
        assert result[0].total_goal_value == 15.8
        assert result[1].player_name == "Player 1"
        assert result[1].total_goal_value == 10.5
        assert result[2].player_name == "Player 2"
        assert result[2].total_goal_value == 5.2

    def test_respects_limit_parameter(self, db_session) -> None:
        """Test that limit parameter is respected."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=5)

        assert len(result) == 5

    def test_filters_by_league_id(self, db_session) -> None:
        """Test that league_id parameter filters results correctly."""
        nation = NationFactory()
        comp1 = CompetitionFactory(name="Premier League", nation=nation)
        comp2 = CompetitionFactory(name="Championship", nation=nation)
        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season1,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season2,
            team=team,
            goal_value=8.0,
            goals_scored=4,
            matches_played=8,
        )

        db_session.commit()

        result = get_by_season(db_session, season1.id, limit=10, league_id=comp1.id)

        assert len(result) == 1
        assert result[0].player_name == player1.name
        assert result[0].total_goal_value == 10.0

    def test_aggregates_team_names(self, db_session) -> None:
        """Test that team names are aggregated and sorted correctly."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Chelsea", nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team1,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team2,
            goal_value=3.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 1
        assert result[0].clubs == "Arsenal, Chelsea"

    def test_handles_duplicate_team_names(self, db_session) -> None:
        """Test that duplicate team names are handled correctly."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Arsenal", nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team1,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team2,
            goal_value=3.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 1
        assert result[0].clubs == "Arsenal"

    def test_displays_clubs_correctly(self, db_session) -> None:
        """Test that clubs are displayed correctly for players with teams."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(name="Arsenal", nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 1
        assert result[0].clubs == "Arsenal"

    def test_excludes_players_with_none_goal_value(self, db_session) -> None:
        """Test that players with None goal_value are excluded."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player_with_value = PlayerFactory(nation=nation)
        player_without_value = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player_with_value,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player_without_value,
            season=season,
            team=team,
            goal_value=None,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 1
        assert result[0].player_name == player_with_value.name

    def test_excludes_players_with_zero_goal_value(self, db_session) -> None:
        """Test that players with zero or negative goal_value are excluded."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player_with_value = PlayerFactory(nation=nation)
        player_with_zero = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player_with_value,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player_with_zero,
            season=season,
            team=team,
            goal_value=0.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 1
        assert result[0].player_name == player_with_value.name

    def test_returns_empty_list_when_season_not_found(self, db_session) -> None:
        """Test that empty list is returned when season doesn't exist."""
        result = get_by_season(db_session, 99999, limit=10)

        assert result == []

    def test_handles_brazilian_season_normalization(self, db_session) -> None:
        """Test that Brazilian single-year seasons are normalized correctly when league_id is None."""
        nation = NationFactory()
        comp = CompetitionFactory(nation=nation)
        brazilian_season = SeasonFactory(competition=comp, start_year=2023, end_year=2023)
        european_season = SeasonFactory(competition=comp, start_year=2022, end_year=2023)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=brazilian_season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=european_season,
            team=team,
            goal_value=3.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_by_season(db_session, brazilian_season.id, limit=10, league_id=None)

        assert len(result) == 1
        assert result[0].total_goal_value == 8.0

    def test_aggregates_stats_across_multiple_teams(self, db_session) -> None:
        """Test that stats are aggregated across multiple teams in same season."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team1 = TeamFactory(nation=nation)
        team2 = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team1,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team2,
            goal_value=7.5,
            goals_scored=3,
            matches_played=6,
        )

        db_session.commit()

        result = get_by_season(db_session, season.id, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 12.5
        assert result[0].total_goals == 5
        assert result[0].total_matches == 11


class TestGetAllSeasons:
    """Tests for get_all_seasons function."""

    def test_returns_top_player_seasons_sorted_by_goal_value(self, db_session) -> None:
        """Test that player-seasons are returned sorted by total goal_value descending."""
        nation = NationFactory()
        _, comp, season1 = create_basic_season_setup(
            db_session, nation=nation, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season1,
            team=team,
            goal_value=15.8,
            goals_scored=7,
            matches_played=12,
        )
        PlayerStatsFactory(
            player=player2,
            season=season1,
            team=team,
            goal_value=10.5,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player1,
            season=season2,
            team=team,
            goal_value=5.2,
            goals_scored=3,
            matches_played=8,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 3
        assert result[0].player_name == "Player 1"
        assert result[0].season_id == season1.id
        assert result[0].total_goal_value == 15.8
        assert result[1].player_name == "Player 2"
        assert result[1].season_id == season1.id
        assert result[1].total_goal_value == 10.5
        assert result[2].player_name == "Player 1"
        assert result[2].season_id == season2.id
        assert result[2].total_goal_value == 5.2

    def test_respects_limit_parameter(self, db_session) -> None:
        """Test that limit parameter is respected."""
        nation = NationFactory()
        _, comp, season1 = create_basic_season_setup(
            db_session, nation=nation, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        for i in range(10):
            player = PlayerFactory(nation=nation)
            PlayerStatsFactory(
                player=player,
                season=season1 if i % 2 == 0 else season2,
                team=team,
                goal_value=float(i + 1),
                goals_scored=1,
                matches_played=1,
            )

        db_session.commit()

        result = get_all_seasons(db_session, limit=5)

        assert len(result) == 5

    def test_filters_by_league_id(self, db_session) -> None:
        """Test that league_id parameter filters results correctly."""
        nation = NationFactory()
        comp1 = CompetitionFactory(name="Premier League", nation=nation)
        comp2 = CompetitionFactory(name="Championship", nation=nation)
        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season1,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season2,
            team=team,
            goal_value=8.0,
            goals_scored=4,
            matches_played=8,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10, league_id=comp1.id)

        assert len(result) == 1
        assert result[0].player_name == player1.name
        assert result[0].season_id == season1.id
        assert result[0].total_goal_value == 10.0

    def test_groups_by_player_and_season(self, db_session) -> None:
        """Test that same player can appear multiple times for different seasons."""
        nation = NationFactory()
        _, comp, season1 = create_basic_season_setup(
            db_session, nation=nation, start_year=2022, end_year=2023
        )
        season2 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(name="Same Player", nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season1,
            team=team,
            goal_value=15.0,
            goals_scored=7,
            matches_played=12,
        )
        PlayerStatsFactory(
            player=player,
            season=season2,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 2
        assert all(r.player_name == "Same Player" for r in result)
        assert result[0].season_id == season1.id
        assert result[0].total_goal_value == 15.0
        assert result[1].season_id == season2.id
        assert result[1].total_goal_value == 10.0

    def test_includes_season_display_name(self, db_session) -> None:
        """Test that season_display_name is included in results."""
        nation = NationFactory()
        _, comp, season = create_basic_season_setup(
            db_session, nation=nation, start_year=2022, end_year=2023
        )
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].season_display_name == "2022/2023"
        assert result[0].season_id == season.id

    def test_handles_single_year_season_display_name(self, db_session) -> None:
        """Test that single-year seasons display correctly."""
        nation = NationFactory()
        comp = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2023)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].season_display_name == "2023"

    def test_aggregates_team_names(self, db_session) -> None:
        """Test that team names are aggregated and sorted correctly."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Chelsea", nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team1,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team2,
            goal_value=3.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].clubs == "Arsenal, Chelsea"

    def test_excludes_players_with_none_goal_value(self, db_session) -> None:
        """Test that players with None goal_value are excluded."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player_with_value = PlayerFactory(nation=nation)
        player_without_value = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player_with_value,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player_without_value,
            season=season,
            team=team,
            goal_value=None,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].player_name == player_with_value.name

    def test_excludes_players_with_zero_goal_value(self, db_session) -> None:
        """Test that players with zero or negative goal_value are excluded."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player_with_value = PlayerFactory(nation=nation)
        player_with_zero = PlayerFactory(nation=nation)

        PlayerStatsFactory(
            player=player_with_value,
            season=season,
            team=team,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player_with_zero,
            season=season,
            team=team,
            goal_value=0.0,
            goals_scored=1,
            matches_played=3,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].player_name == player_with_value.name

    def test_calculates_goal_value_avg(self, db_session) -> None:
        """Test that goal_value_avg is calculated correctly."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].goal_value_avg == 2.0

    def test_rounds_decimal_values(self, db_session) -> None:
        """Test that decimal values are rounded to two decimals."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team,
            goal_value=10.123456,
            goals_scored=3,
            matches_played=5,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 10.12
        assert result[0].goal_value_avg == 3.37

    def test_aggregates_stats_across_multiple_teams_in_same_season(self, db_session) -> None:
        """Test that stats are aggregated across multiple teams in same season."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team1 = TeamFactory(nation=nation)
        team2 = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team1,
            goal_value=5.0,
            goals_scored=2,
            matches_played=5,
        )
        PlayerStatsFactory(
            player=player,
            season=season,
            team=team2,
            goal_value=7.5,
            goals_scored=3,
            matches_played=6,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 1
        assert result[0].total_goal_value == 12.5
        assert result[0].total_goals == 5
        assert result[0].total_matches == 11

    def test_sorts_by_goal_value_avg_as_secondary_sort(self, db_session) -> None:
        """Test that secondary sort by goal_value_avg works correctly (descending)."""
        nation = NationFactory()
        _, _, season = create_basic_season_setup(db_session, nation=nation)
        team = TeamFactory(nation=nation)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)

        PlayerStatsFactory(
            player=player1,
            season=season,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player2,
            season=season,
            team=team,
            goal_value=10.0,
            goals_scored=4,
            matches_played=10,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10)

        assert len(result) == 2
        assert result[0].total_goal_value == 10.0
        assert result[0].goal_value_avg == 2.5
        assert result[1].total_goal_value == 10.0
        assert result[1].goal_value_avg == 2.0

    def test_returns_empty_list_when_no_data(self, db_session) -> None:
        """Test that empty list is returned when no player-seasons exist."""
        result = get_all_seasons(db_session, limit=10)

        assert result == []

    def test_filters_by_league_only_shows_seasons_from_that_league(self, db_session) -> None:
        """Test that league filter only shows seasons from that specific league."""
        nation = NationFactory()
        comp1 = CompetitionFactory(name="Premier League", nation=nation)
        comp2 = CompetitionFactory(name="Championship", nation=nation)
        season1 = SeasonFactory(competition=comp1, start_year=2022, end_year=2023)
        season2 = SeasonFactory(competition=comp2, start_year=2022, end_year=2023)
        team = TeamFactory(nation=nation)

        player = PlayerFactory(nation=nation)
        PlayerStatsFactory(
            player=player,
            season=season1,
            team=team,
            goal_value=10.0,
            goals_scored=5,
            matches_played=10,
        )
        PlayerStatsFactory(
            player=player,
            season=season2,
            team=team,
            goal_value=8.0,
            goals_scored=4,
            matches_played=8,
        )

        db_session.commit()

        result = get_all_seasons(db_session, limit=10, league_id=comp1.id)

        assert len(result) == 1
        assert result[0].season_id == season1.id
        assert result[0].total_goal_value == 10.0
