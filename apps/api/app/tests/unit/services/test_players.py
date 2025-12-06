"""Unit tests for players service layer."""

from datetime import date

from app.services.players import (
    get_player_career_goal_log,
    get_player_seasons_stats,
    transform_player_stats,
)
from app.tests.utils.factories import (
    MatchFactory,
    PlayerFactory,
    PlayerStatsFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.tests.utils.helpers import (
    create_assist_event,
    create_basic_season_setup,
    create_goal_event,
)


class TestTransformPlayerStats:
    """Tests for transform_player_stats helper."""

    def test_rounds_decimal_fields(self):
        """Test that decimal fields are rounded to two decimals."""
        stats = PlayerStatsFactory.build(
            matches_played=30,
            matches_started=25,
            total_minutes=2500,
            minutes_divided_90=12.3456,
            goals_scored=15,
            assists=7,
            total_goal_assists=22,
            non_pk_goals=14,
            pk_made=2,
            pk_attempted=3,
            yellow_cards=3,
            red_cards=0,
            goal_value=1.234,
            gv_avg=0.0567,
            goal_per_90=0.9876,
            assists_per_90=0.5432,
            total_goals_assists_per_90=1.5308,
            non_pk_goals_per_90=0.4567,
            non_pk_goal_and_assists_per_90=1.4321,
        )

        result = transform_player_stats(stats)

        assert result.minutes_divided_90 == 12.35
        assert result.goal_value == 1.23
        assert result.gv_avg == 0.06
        assert result.goal_per_90 == 0.99
        assert result.assists_per_90 == 0.54
        assert result.total_goals_assists_per_90 == 1.53
        assert result.non_pk_goals_per_90 == 0.46
        assert result.non_pk_goal_and_assists_per_90 == 1.43

    def test_handles_none_and_zero_values(self):
        """Test that None/zero values remain None after transformation."""
        stats = PlayerStatsFactory.build(
            matches_played=None,
            matches_started=None,
            total_minutes=None,
            minutes_divided_90=0,
            goals_scored=None,
            assists=None,
            total_goal_assists=None,
            non_pk_goals=None,
            pk_made=None,
            pk_attempted=None,
            yellow_cards=None,
            red_cards=None,
            goal_value=None,
            gv_avg=None,
            goal_per_90=None,
            assists_per_90=None,
            total_goals_assists_per_90=None,
            non_pk_goals_per_90=None,
            non_pk_goal_and_assists_per_90=None,
        )

        result = transform_player_stats(stats)

        assert result.minutes_divided_90 is None
        assert result.goal_value is None
        assert result.gv_avg is None
        assert result.goal_per_90 is None
        assert result.assists_per_90 is None
        assert result.total_goals_assists_per_90 is None
        assert result.non_pk_goals_per_90 is None
        assert result.non_pk_goal_and_assists_per_90 is None


class TestGetPlayerSeasonsStats:
    """Tests for get_player_seasons_stats."""

    def test_returns_none_when_player_not_found(self, db_session):
        """Test that None and empty list are returned when player is missing."""
        player_info, seasons = get_player_seasons_stats(db_session, 999999)

        assert player_info is None
        assert seasons == []

    def test_returns_player_info_with_sorted_seasons(self, db_session):
        """Test that player info and seasons are returned in sorted order."""
        player = PlayerFactory(name="Star Player")
        nation = player.nation

        team1 = TeamFactory(name="Club A", nation=nation)
        team2 = TeamFactory(name="Club B", nation=nation)
        team3 = TeamFactory(name="Club C", nation=nation)

        _, _, season1 = create_basic_season_setup(
            db_session,
            nation=nation,
            comp_name="League A",
            start_year=2022,
            end_year=2023,
        )
        _, _, season2 = create_basic_season_setup(
            db_session,
            nation=nation,
            comp_name="League B",
            start_year=2023,
            end_year=2024,
        )
        _, _, season3 = create_basic_season_setup(
            db_session,
            nation=nation,
            comp_name="League C",
            start_year=2023,
            end_year=2024,
        )

        PlayerStatsFactory(
            player=player,
            team=team1,
            season=season1,
            matches_played=30,
            goal_value=1.234,
            gv_avg=0.0567,
            goal_per_90=0.9876,
            assists_per_90=0.5432,
            total_goals_assists_per_90=1.5308,
            non_pk_goals_per_90=0.4567,
            non_pk_goal_and_assists_per_90=1.4321,
        )
        PlayerStatsFactory(
            player=player,
            team=team2,
            season=season2,
            matches_played=34,
            goal_value=2.345,
            gv_avg=0.0789,
            goal_per_90=0.6543,
            assists_per_90=0.2109,
            total_goals_assists_per_90=0.8652,
            non_pk_goals_per_90=0.4321,
            non_pk_goal_and_assists_per_90=0.643,
        )
        PlayerStatsFactory(
            player=player,
            team=team3,
            season=season3,
            matches_played=10,
            goal_value=None,
            gv_avg=None,
        )

        TeamStatsFactory(team=team1, season=season1, ranking=1)
        TeamStatsFactory(team=team2, season=season2, ranking=2)

        match1 = MatchFactory(
            season=season1,
            home_team=team1,
            away_team=TeamFactory(nation=nation),
            date=date(2022, 8, 10),
        )
        create_goal_event(
            match1, player, minute=15, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        match2 = MatchFactory(
            season=season2,
            home_team=TeamFactory(nation=nation),
            away_team=team2,
            date=date(2023, 8, 5),
        )
        create_goal_event(
            match2, player, minute=30, home_pre=0, home_post=0, away_pre=0, away_post=1
        )

        player_info, seasons = get_player_seasons_stats(db_session, player.id)

        assert player_info is not None
        assert player_info.name == "Star Player"
        assert player_info.nation.name == nation.name

        team_order = [season.team.name for season in seasons]
        assert team_order == [team1.name, team2.name, team3.name]

        assert seasons[0].league_rank == 1
        assert seasons[1].league_rank == 2
        assert seasons[2].league_rank is None

        assert seasons[0].stats.goal_value == 1.23
        assert seasons[1].stats.goal_value == 2.35
        assert seasons[2].stats.goal_value is None
        assert seasons[0].season.display_name == "2022/2023"

    def test_returns_player_info_without_stats(self, db_session):
        """Test that player info is returned even when stats are missing."""
        player = PlayerFactory(name="No Stats Player")

        player_info, seasons = get_player_seasons_stats(db_session, player.id)

        assert player_info is not None
        assert player_info.name == "No Stats Player"
        assert seasons == []


class TestGetPlayerCareerGoalLog:
    """Tests for get_player_career_goal_log."""

    def test_returns_none_when_player_not_found(self, db_session):
        """Test that None and empty list are returned when player is missing."""
        player_basic, goal_entries = get_player_career_goal_log(db_session, 999999)

        assert player_basic is None
        assert goal_entries == []

    def test_returns_empty_goals_when_player_has_no_events(self, db_session):
        """Test that empty goal list is returned when player has no goal events."""
        player = PlayerFactory(name="No Goal Player")

        player_basic, goal_entries = get_player_career_goal_log(db_session, player.id)

        assert player_basic is not None
        assert player_basic.name == "No Goal Player"
        assert goal_entries == []

    def test_returns_sorted_goal_entries_with_assists(self, db_session):
        """Test that goal log entries are returned with proper sorting and assists."""
        player = PlayerFactory(name="Clutch Scorer")
        nation = player.nation

        _, _, season1 = create_basic_season_setup(
            db_session,
            nation=nation,
            comp_name="League A",
            start_year=2022,
            end_year=2023,
        )
        _, _, season2 = create_basic_season_setup(
            db_session,
            nation=nation,
            comp_name="League B",
            start_year=2023,
            end_year=2024,
        )

        team_home = TeamFactory(name="Home FC", nation=nation)
        team_away = TeamFactory(name="Away FC", nation=nation)
        opponent1 = TeamFactory(name="Opponent One", nation=nation)
        opponent2 = TeamFactory(name="Opponent Two", nation=nation)

        match1 = MatchFactory(
            season=season1,
            home_team=team_home,
            away_team=opponent1,
            date=date(2023, 5, 1),
        )
        match2 = MatchFactory(
            season=season2,
            home_team=opponent2,
            away_team=team_away,
            date=date(2024, 3, 1),
        )

        assist_player = PlayerFactory(name="Playmaker", nation=nation)
        create_assist_event(
            match1, assist_player, minute=15, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        create_goal_event(
            match1,
            player,
            minute=15,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=0.75,
            xg=0.35,
            post_shot_xg=0.4,
        )
        create_goal_event(
            match2,
            player,
            minute=55,
            home_pre=0,
            home_post=0,
            away_pre=0,
            away_post=1,
            goal_value=0.5,
            xg=0.25,
            post_shot_xg=0.3,
        )

        player_basic, goal_entries = get_player_career_goal_log(db_session, player.id)

        assert player_basic is not None
        assert player_basic.name == "Clutch Scorer"
        assert len(goal_entries) == 2

        first_goal, second_goal = goal_entries

        assert first_goal.team.name == "Home FC"
        assert first_goal.opponent.name == "Opponent One"
        assert first_goal.venue == "Home"
        assert first_goal.score_before == "0-0"
        assert first_goal.score_after == "1-0"
        assert first_goal.date == "01/05/2023"
        assert first_goal.assisted_by is not None
        assert first_goal.assisted_by.name == "Playmaker"

        assert second_goal.team.name == "Away FC"
        assert second_goal.opponent.name == "Opponent Two"
        assert second_goal.venue == "Away"
        assert second_goal.score_before == "0-0"
        assert second_goal.score_after == "0-1"
        assert second_goal.date == "01/03/2024"
        assert second_goal.assisted_by is None
