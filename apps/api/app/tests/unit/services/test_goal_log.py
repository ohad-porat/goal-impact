"""Unit tests for goal log service utilities."""

from datetime import date
from app.services.goal_log import (
    is_goal_for_team,
    format_score,
    get_assist_for_goal_from_data,
    format_scorer_name,
    get_venue_for_team,
    build_team_season_goal_log_entry_from_data,
    sort_and_format_team_season_goal_entries,
    build_player_career_goal_log_entry_from_data,
    sort_and_format_player_career_goal_entries,
)
from app.schemas.clubs import (
    GoalLogEntry,
    PlayerBasic,
    PlayerGoalLogEntry,
    ClubInfo,
    NationDetailed,
)
from app.tests.utils.factories import (
    EventFactory,
    MatchFactory,
    PlayerFactory,
    TeamFactory,
)


def create_match_with_teams(db_session, home_team_name=None, away_team_name=None, **match_kwargs):
    """Helper to create a match with home and away teams."""
    home_team = TeamFactory(name=home_team_name) if home_team_name else TeamFactory()
    away_team = TeamFactory(name=away_team_name) if away_team_name else TeamFactory()
    match = MatchFactory(home_team=home_team, away_team=away_team, **match_kwargs)
    db_session.commit()
    return home_team, away_team, match


def create_goal_event(match, scorer=None, event_type="goal", 
                     pre_home=0, pre_away=0, post_home=1, post_away=0, **kwargs):
    """Helper to create a goal event with standardized goal tracking fields."""
    return EventFactory(
        match=match,
        event_type=event_type,
        player=scorer,
        home_team_goals_pre_event=pre_home,
        away_team_goals_pre_event=pre_away,
        home_team_goals_post_event=post_home,
        away_team_goals_post_event=post_away,
        **kwargs
    )


def create_club_info(id, name, nation_id=1, nation_name="Nation", country_code="XX"):
    """Helper to create ClubInfo with NationDetailed."""
    return ClubInfo(
        id=id,
        name=name,
        nation=NationDetailed(id=nation_id, name=nation_name, country_code=country_code)
    )


class TestIsGoalForTeam:
    """Test is_goal_for_team function."""

    def test_goal_for_home_team(self, db_session):
        """Test identifying goal scored by home team."""
        home_team, _, match = create_match_with_teams(db_session)
        goal_event = create_goal_event(match, pre_home=0, pre_away=0, post_home=1, post_away=0)
        db_session.commit()

        result = is_goal_for_team(goal_event, match, home_team.id)

        assert result is True

    def test_goal_for_away_team(self, db_session):
        """Test identifying goal scored by away team."""
        _, away_team, match = create_match_with_teams(db_session)
        goal_event = create_goal_event(match, pre_home=0, pre_away=0, post_home=0, post_away=1)
        db_session.commit()

        result = is_goal_for_team(goal_event, match, away_team.id)

        assert result is True

    def test_goal_returns_false_when_team_not_in_match(self, db_session):
        """Test that goal returns False when checking a team that wasn't playing in the match."""
        _, _, match = create_match_with_teams(db_session)
        other_team = TeamFactory()
        goal_event = create_goal_event(match, pre_home=0, pre_away=0, post_home=1, post_away=0)
        db_session.commit()

        result = is_goal_for_team(goal_event, match, other_team.id)

        assert result is False

    def test_returns_false_when_goals_pre_event_none(self, db_session):
        """Test returns False when home_team_goals_pre_event is None."""
        home_team, _, match = create_match_with_teams(db_session)
        goal_event = create_goal_event(match, pre_home=None, pre_away=0, post_home=1, post_away=0)
        db_session.commit()

        result = is_goal_for_team(goal_event, match, home_team.id)

        assert result is False

    def test_returns_false_when_goals_post_event_none(self, db_session):
        """Test returns False when home_team_goals_post_event is None."""
        home_team, _, match = create_match_with_teams(db_session)
        goal_event = create_goal_event(match, pre_home=0, pre_away=0, post_home=None, post_away=0)
        db_session.commit()

        result = is_goal_for_team(goal_event, match, home_team.id)

        assert result is False


class TestFormatScore:
    """Test format_score function."""

    def test_format_score_with_valid_data(self, db_session):
        """Test formatting score with all valid data."""
        match = MatchFactory()
        goal_event = create_goal_event(match, pre_home=1, pre_away=0, post_home=2, post_away=0)
        db_session.commit()

        score_before, score_after = format_score(goal_event)

        assert score_before == "1-0"
        assert score_after == "2-0"

    def test_format_score_returns_empty_strings_when_none(self, db_session):
        """Test formatting score returns empty strings when data is None."""
        match = MatchFactory()
        goal_event = create_goal_event(
            match, pre_home=None, pre_away=None, post_home=None, post_away=None
        )
        db_session.commit()

        score_before, score_after = format_score(goal_event)

        assert score_before == ""
        assert score_after == ""


class TestGetAssistForGoalFromData:
    """Test get_assist_for_goal_from_data function."""

    def test_get_assist_with_event_and_player_present(self, db_session):
        """Test getting assist when both assist_event and assist_player are present."""
        assist_player = PlayerFactory(name="Assist Player")
        assist_event = EventFactory(event_type="assist")
        db_session.commit()

        result = get_assist_for_goal_from_data(assist_event, assist_player)

        assert result is not None
        assert isinstance(result, PlayerBasic)
        assert result.id == assist_player.id
        assert result.name == "Assist Player"

    def test_get_assist_returns_none_when_event_none(self, db_session):
        """Test returns None when assist_event is None."""
        assist_player = PlayerFactory()
        db_session.commit()

        result = get_assist_for_goal_from_data(None, assist_player)

        assert result is None

    def test_get_assist_returns_none_when_player_none(self, db_session):
        """Test returns None when assist_player is None."""
        assist_event = EventFactory()
        db_session.commit()

        result = get_assist_for_goal_from_data(assist_event, None)

        assert result is None

    def test_get_assist_returns_none_when_both_none(self):
        """Test returns None when both are None."""
        result = get_assist_for_goal_from_data(None, None)
        assert result is None


class TestFormatScorerName:
    """Test format_scorer_name function."""

    def test_format_scorer_name_regular_goal(self, db_session):
        """Test formatting scorer name for regular goal."""
        scorer = PlayerFactory(name="Lionel Messi")
        db_session.commit()

        result = format_scorer_name(scorer, "goal")

        assert result == "Lionel Messi"

    def test_format_scorer_name_own_goal(self, db_session):
        """Test formatting scorer name for own goal."""
        scorer = PlayerFactory(name="John Doe")
        db_session.commit()

        result = format_scorer_name(scorer, "own goal")

        assert result == "John Doe (OG)"


class TestGetVenueForTeam:
    """Test get_venue_for_team function."""

    def test_get_venue_for_home_team(self, db_session):
        """Test getting venue for home team."""
        home_team, _, match = create_match_with_teams(db_session)

        result = get_venue_for_team(match, home_team.id)

        assert result == "Home"

    def test_get_venue_for_away_team(self, db_session):
        """Test getting venue for away team."""
        _, away_team, match = create_match_with_teams(db_session)

        result = get_venue_for_team(match, away_team.id)

        assert result == "Away"


class TestBuildTeamSeasonGoalLogEntryFromData:
    """Test build_team_season_goal_log_entry_from_data function."""

    def test_build_entry_for_team_goal(self, db_session):
        """Test building goal log entry for team's goal."""
        home_team, away_team, match = create_match_with_teams(
            db_session, home_team_name="Arsenal", away_team_name="Chelsea"
        )
        scorer = PlayerFactory(name="Goal Scorer")
        goal_event = create_goal_event(
            match, scorer=scorer, minute=45,
            pre_home=1, pre_away=0, post_home=2, post_away=0,
            goal_value=0.5, xg=0.3, post_shot_xg=0.4
        )
        db_session.commit()

        result = build_team_season_goal_log_entry_from_data(
            goal_event, match, scorer, home_team.id, away_team
        )

        assert result is not None
        assert isinstance(result, GoalLogEntry)
        assert result.venue == "Home"
        assert result.scorer.id == scorer.id
        assert result.scorer.name == "Goal Scorer"
        assert result.opponent.name == "Chelsea"
        assert result.minute == 45
        assert result.score_before == "1-0"
        assert result.score_after == "2-0"
        assert result.goal_value == 0.5
        assert result.xg == 0.3
        assert result.post_shot_xg == 0.4

    def test_build_entry_returns_none_when_goal_not_for_specified_team(self, db_session):
        """Test returns None when the goal was not scored for the specified team."""
        _, away_team, match = create_match_with_teams(db_session)
        other_team = TeamFactory()
        scorer = PlayerFactory()
        goal_event = create_goal_event(match, scorer=scorer, pre_home=0, pre_away=0, post_home=1, post_away=0)
        db_session.commit()

        result = build_team_season_goal_log_entry_from_data(
            goal_event, match, scorer, other_team.id, away_team
        )

        assert result is None

    def test_build_entry_returns_none_when_opponent_none(self, db_session):
        """Test returns None when opponent_team is None."""
        home_team, _, match = create_match_with_teams(db_session)
        scorer = PlayerFactory()
        goal_event = create_goal_event(match, scorer=scorer, pre_home=0, pre_away=0, post_home=1, post_away=0)
        db_session.commit()

        result = build_team_season_goal_log_entry_from_data(
            goal_event, match, scorer, home_team.id, None
        )

        assert result is None

    def test_build_entry_for_own_goal(self, db_session):
        """Test building entry for own goal."""
        home_team, away_team, match = create_match_with_teams(db_session)
        scorer = PlayerFactory(name="Unlucky Player")
        goal_event = create_goal_event(
            match, scorer=scorer, event_type="own goal",
            pre_home=0, pre_away=0, post_home=0, post_away=1,
            goal_value=0.2
        )
        db_session.commit()

        result = build_team_season_goal_log_entry_from_data(
            goal_event, match, scorer, away_team.id, home_team
        )

        assert result is not None
        assert result.scorer.name == "Unlucky Player (OG)"

    def test_build_entry_with_assist(self, db_session):
        """Test building entry with assist information."""
        home_team, away_team, match = create_match_with_teams(db_session)
        scorer = PlayerFactory(name="Scorer")
        assist_player = PlayerFactory(name="Assister")
        goal_event = create_goal_event(match, scorer=scorer, pre_home=0, pre_away=0, post_home=1, post_away=0)
        assist_event = EventFactory(match=match, event_type="assist", player=assist_player)
        db_session.commit()

        result = build_team_season_goal_log_entry_from_data(
            goal_event, match, scorer, home_team.id, away_team,
            assist_event, assist_player
        )

        assert result is not None
        assert result.assisted_by is not None
        assert result.assisted_by.name == "Assister"


class TestSortAndFormatTeamSeasonGoalEntries:
    """Test sort_and_format_team_season_goal_entries function."""

    def test_sort_entries_by_date_and_minute(self):
        """Test sorting entries by date and minute."""
        date1 = date(2023, 1, 15)
        date2 = date(2023, 1, 20)
        date3 = date(2023, 1, 15)

        entry1 = GoalLogEntry(
            date="",
            venue="Home",
            scorer=PlayerBasic(id=1, name="Player 1"),
            opponent=create_club_info(id=1, name="Opponent", nation_id=1, nation_name="Nation", country_code="XX"),
            minute=30,
            score_before="0-0",
            score_after="1-0",
            goal_value=0.5,
            xg=None,
            post_shot_xg=None,
            assisted_by=None
        )
        entry2 = GoalLogEntry(
            date="",
            venue="Away",
            scorer=PlayerBasic(id=2, name="Player 2"),
            opponent=create_club_info(id=2, name="Opponent 2", nation_id=2, nation_name="Nation 2", country_code="YY"),
            minute=60,
            score_before="1-0",
            score_after="2-0",
            goal_value=0.6,
            xg=None,
            post_shot_xg=None,
            assisted_by=None
        )
        entry3 = GoalLogEntry(
            date="",
            venue="Home",
            scorer=PlayerBasic(id=3, name="Player 3"),
            opponent=create_club_info(id=3, name="Opponent 3", nation_id=3, nation_name="Nation 3", country_code="ZZ"),
            minute=15,
            score_before="0-0",
            score_after="1-0",
            goal_value=0.4,
            xg=None,
            post_shot_xg=None,
            assisted_by=None
        )

        entries_with_date = [
            (date1, entry1),
            (date2, entry2),
            (date3, entry3),
        ]

        result = sort_and_format_team_season_goal_entries(entries_with_date)

        assert len(result) == 3
        assert result[0].minute == 15
        assert result[1].minute == 30
        assert result[2].minute == 60
        assert result[0].date == "15/01/2023"
        assert result[1].date == "15/01/2023"
        assert result[2].date == "20/01/2023"


class TestBuildPlayerCareerGoalLogEntryFromData:
    """Test build_player_career_goal_log_entry_from_data function."""

    def test_build_entry_for_player_goal(self, db_session):
        """Test building goal log entry for player's goal."""
        player_team, opponent_team, match = create_match_with_teams(
            db_session, home_team_name="Arsenal", away_team_name="Chelsea", season_id=1
        )
        scorer = PlayerFactory(name="Goal Scorer")
        goal_event = create_goal_event(
            match, scorer=scorer, minute=45,
            pre_home=1, pre_away=0, post_home=2, post_away=0,
            goal_value=0.5, xg=0.3, post_shot_xg=0.4
        )
        db_session.commit()

        result = build_player_career_goal_log_entry_from_data(
            goal_event, match, scorer, "2023/2024", player_team, opponent_team
        )

        assert result is not None
        assert isinstance(result, PlayerGoalLogEntry)
        assert result.venue == "Home"
        assert result.team.name == "Arsenal"
        assert result.opponent.name == "Chelsea"
        assert result.minute == 45
        assert result.score_before == "1-0"
        assert result.score_after == "2-0"
        assert result.goal_value == 0.5
        assert result.season_id == 1
        assert result.season_display_name == "2023/2024"

    def test_build_entry_returns_none_when_player_team_none(self, db_session):
        """Test returns None when player_team is None."""
        opponent_team = TeamFactory()
        scorer = PlayerFactory()
        match = MatchFactory()
        goal_event = EventFactory(match=match, player=scorer)
        db_session.commit()

        result = build_player_career_goal_log_entry_from_data(
            goal_event, match, scorer, "2023/2024", None, opponent_team
        )

        assert result is None

    def test_build_entry_returns_none_when_opponent_team_none(self, db_session):
        """Test returns None when opponent_team is None."""
        player_team = TeamFactory()
        scorer = PlayerFactory()
        match = MatchFactory()
        goal_event = EventFactory(match=match, player=scorer)
        db_session.commit()

        result = build_player_career_goal_log_entry_from_data(
            goal_event, match, scorer, "2023/2024", player_team, None
        )

        assert result is None

    def test_build_entry_with_assist(self, db_session):
        """Test building entry with assist information."""
        player_team, opponent_team, match = create_match_with_teams(db_session, season_id=1)
        scorer = PlayerFactory(name="Scorer")
        assist_player = PlayerFactory(name="Assister")
        goal_event = create_goal_event(
            match, scorer=scorer,
            pre_home=0, pre_away=0, post_home=1, post_away=0
        )
        assist_event = EventFactory(
            match=match,
            event_type="assist",
            player=assist_player
        )
        db_session.commit()

        result = build_player_career_goal_log_entry_from_data(
            goal_event, match, scorer, "2023/2024", player_team, opponent_team,
            assist_event, assist_player
        )

        assert result is not None
        assert result.assisted_by is not None
        assert result.assisted_by.name == "Assister"


class TestSortAndFormatPlayerCareerGoalEntries:
    """Test sort_and_format_player_career_goal_entries function."""

    def test_sort_entries_by_season_date_and_minute(self):
        """Test sorting entries by season, date and minute."""
        entry1 = PlayerGoalLogEntry(
            date="",
            venue="Home",
            team=create_club_info(id=1, name="Team 1", nation_id=1, nation_name="Nation", country_code="XX"),
            opponent=create_club_info(id=2, name="Opponent 1", nation_id=2, nation_name="Nation 2", country_code="YY"),
            minute=30,
            score_before="0-0",
            score_after="1-0",
            goal_value=0.5,
            xg=None,
            post_shot_xg=None,
            assisted_by=None,
            season_id=1,
            season_display_name="2022/2023"
        )
        entry2 = PlayerGoalLogEntry(
            date="",
            venue="Away",
            team=create_club_info(id=1, name="Team 1", nation_id=1, nation_name="Nation", country_code="XX"),
            opponent=create_club_info(id=3, name="Opponent 2", nation_id=3, nation_name="Nation 3", country_code="ZZ"),
            minute=60,
            score_before="1-0",
            score_after="2-0",
            goal_value=0.6,
            xg=None,
            post_shot_xg=None,
            assisted_by=None,
            season_id=2,
            season_display_name="2023/2024"
        )
        entry3 = PlayerGoalLogEntry(
            date="",
            venue="Home",
            team=create_club_info(id=1, name="Team 1", nation_id=1, nation_name="Nation", country_code="XX"),
            opponent=create_club_info(id=4, name="Opponent 3", nation_id=4, nation_name="Nation 4", country_code="AA"),
            minute=15,
            score_before="0-0",
            score_after="1-0",
            goal_value=0.4,
            xg=None,
            post_shot_xg=None,
            assisted_by=None,
            season_id=1,
            season_display_name="2022/2023"
        )

        entries_with_date_season = [
            (date(2023, 1, 15), 1, entry1),
            (date(2023, 6, 20), 2, entry2),
            (date(2022, 12, 10), 1, entry3),
        ]

        result = sort_and_format_player_career_goal_entries(entries_with_date_season)

        assert len(result) == 3
        assert result[0].minute == 15
        assert result[1].minute == 30
        assert result[2].minute == 60
        assert result[0].date == "10/12/2022"
        assert result[1].date == "15/01/2023"
        assert result[2].date == "20/06/2023"
