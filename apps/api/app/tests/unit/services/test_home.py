"""Unit tests for home service layer."""

from datetime import date, timedelta

from app.services.home import get_recent_impact_goals
from app.tests.utils.factories import (
    NationFactory,
    CompetitionFactory,
    SeasonFactory,
    TeamFactory,
    PlayerFactory,
    MatchFactory,
    EventFactory,
)
from app.tests.utils.service_helpers import create_basic_season_setup, create_goal_event


class TestGetRecentImpactGoals:
    """Tests for get_recent_impact_goals function."""

    def test_returns_empty_list_when_no_matches(self, db_session):
        """Test that empty list is returned when no matches exist."""
        result = get_recent_impact_goals(db_session)
        
        assert result == []

    def test_returns_top_goals_by_goal_value(self, db_session):
        """Test that top goals are returned sorted by goal value."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player1, 10, 0, 1, 0, 0, goal_value=5.5)
        create_goal_event(match, player2, 20, 1, 2, 0, 0, goal_value=8.2)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 2
        assert result[0].goal_value == 8.2
        assert result[0].scorer.name == player2.name
        assert result[1].goal_value == 5.5
        assert result[1].scorer.name == player1.name

    def test_respects_limit_parameter(self, db_session):
        """Test that limit parameter is respected."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        for i in range(10):
            player = PlayerFactory(nation=nation)
            create_goal_event(match, player, 10 + i, 0, 1, 0, 0, goal_value=float(i))
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 5

    def test_filters_by_days_parameter(self, db_session):
        """Test that goals are filtered by days parameter."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)
        
        recent_date = date.today()
        old_date = date.today() - timedelta(days=10)
        
        recent_match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=recent_date)
        old_match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=old_date)
        
        create_goal_event(recent_match, player1, 10, 0, 1, 0, 0, goal_value=5.5)
        create_goal_event(old_match, player2, 20, 0, 1, 0, 0, goal_value=8.2)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1
        assert result[0].scorer.name == player1.name

    def test_includes_goals_within_date_range(self, db_session):
        """Test that goals within date range are included."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date.today() - timedelta(days=3)
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player, 10, 0, 1, 0, 0, goal_value=5.5)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1

    def test_filters_by_league_id(self, db_session):
        """Test that goals are filtered by league_id when provided."""
        nation = NationFactory()
        comp1 = CompetitionFactory(name="Premier League", nation=nation)
        comp2 = CompetitionFactory(name="La Liga", nation=nation)
        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match1 = MatchFactory(home_team=home_team, away_team=away_team, season=season1, date=match_date)
        match2 = MatchFactory(home_team=home_team, away_team=away_team, season=season2, date=match_date)
        
        create_goal_event(match1, player1, 10, 0, 1, 0, 0, goal_value=5.5)
        create_goal_event(match2, player2, 20, 0, 1, 0, 0, goal_value=8.2)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5, league_id=comp1.id)
        
        assert len(result) == 1
        assert result[0].scorer.name == player1.name

    def test_includes_own_goals(self, db_session):
        """Test that own goals are included in results."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player, 10, 0, 1, 0, 0, event_type="own goal", goal_value=3.5)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1

    def test_excludes_goals_without_goal_value(self, db_session):
        """Test that goals without goal_value are excluded."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        EventFactory(
            match=match,
            player=player,
            event_type="goal",
            minute=10,
            home_team_goals_pre_event=0,
            home_team_goals_post_event=1,
            away_team_goals_pre_event=0,
            away_team_goals_post_event=0,
            goal_value=None
        )
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert result == []

    def test_formats_match_date_correctly(self, db_session):
        """Test that match date is formatted correctly."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date(2024, 3, 15)
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player, 10, 0, 1, 0, 0, goal_value=5.5)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1
        assert result[0].match.date == "March 15, 2024"

    def test_formats_score_before_and_after(self, db_session):
        """Test that score before and after are formatted correctly."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player, 10, 1, 2, 0, 0, goal_value=5.5)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1
        assert result[0].score_before == "1-0"
        assert result[0].score_after == "2-0"

    def test_sorts_results_by_date_descending(self, db_session):
        """Test that results are sorted by date descending."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player1 = PlayerFactory(nation=nation)
        player2 = PlayerFactory(nation=nation)
        player3 = PlayerFactory(nation=nation)
        
        date1 = date.today() - timedelta(days=1)
        date2 = date.today() - timedelta(days=2)
        date3 = date.today() - timedelta(days=3)
        
        match1 = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=date1)
        match2 = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=date2)
        match3 = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=date3)
        
        create_goal_event(match1, player1, 10, 0, 1, 0, 0, goal_value=5.5)
        create_goal_event(match2, player2, 20, 0, 1, 0, 0, goal_value=8.2)
        create_goal_event(match3, player3, 30, 0, 1, 0, 0, goal_value=6.0)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 3
        assert result[0].scorer.name == player1.name
        assert result[1].scorer.name == player2.name
        assert result[2].scorer.name == player3.name

    def test_includes_team_names(self, db_session):
        """Test that team names are included in match info."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(name="Home FC", nation=nation)
        away_team = TeamFactory(name="Away FC", nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player, 10, 0, 1, 0, 0, goal_value=5.5)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1
        assert result[0].match.home_team == "Home FC"
        assert result[0].match.away_team == "Away FC"

    def test_includes_minute(self, db_session):
        """Test that minute is included in result."""
        nation, comp, season = create_basic_season_setup(db_session)
        home_team = TeamFactory(nation=nation)
        away_team = TeamFactory(nation=nation)
        player = PlayerFactory(nation=nation)
        
        match_date = date.today()
        match = MatchFactory(home_team=home_team, away_team=away_team, season=season, date=match_date)
        
        create_goal_event(match, player, 45, 0, 1, 0, 0, goal_value=5.5)
        
        db_session.commit()
        
        result = get_recent_impact_goals(db_session, days=7, limit=5)
        
        assert len(result) == 1
        assert result[0].minute == 45

