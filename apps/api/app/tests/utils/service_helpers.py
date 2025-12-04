"""Shared test helpers for service layer tests."""

from app.tests.utils.factories import (
    CompetitionFactory,
    EventFactory,
    MatchFactory,
    NationFactory,
    SeasonFactory,
    TeamFactory,
)


def create_match_with_teams(db_session, home_team_name=None, away_team_name=None, **match_kwargs):
    """Create a match with home and away teams."""
    home_team = TeamFactory(name=home_team_name) if home_team_name else TeamFactory()
    away_team = TeamFactory(name=away_team_name) if away_team_name else TeamFactory()
    match = MatchFactory(home_team=home_team, away_team=away_team, **match_kwargs)
    db_session.commit()
    return home_team, away_team, match


def create_basic_season_setup(
    db_session, nation=None, comp_name="Premier League", tier="1st", start_year=2023, end_year=2024
):
    """Create a basic season setup (nation, competition, season)."""
    if nation is None:
        nation = NationFactory()
    comp = CompetitionFactory(name=comp_name, tier=tier, nation=nation)
    season = SeasonFactory(competition=comp, start_year=start_year, end_year=end_year)
    db_session.commit()
    return nation, comp, season


def create_goal_event(
    match,
    player,
    minute,
    home_pre,
    home_post,
    away_pre,
    away_post,
    event_type="goal",
    goal_value=None,
    xg=None,
    post_shot_xg=None,
    **kwargs,
):
    """Create a goal event with standardized goal tracking fields."""
    return EventFactory(
        match=match,
        player=player,
        event_type=event_type,
        minute=minute,
        home_team_goals_pre_event=home_pre,
        home_team_goals_post_event=home_post,
        away_team_goals_pre_event=away_pre,
        away_team_goals_post_event=away_post,
        goal_value=goal_value,
        xg=xg,
        post_shot_xg=post_shot_xg,
        **kwargs,
    )


def create_assist_event(match, player, minute, home_pre, home_post, away_pre, away_post, **kwargs):
    """Create an assist event with standardized goal tracking fields."""
    return EventFactory(
        match=match,
        player=player,
        event_type="assist",
        minute=minute,
        home_team_goals_pre_event=home_pre,
        home_team_goals_post_event=home_post,
        away_team_goals_pre_event=away_pre,
        away_team_goals_post_event=away_post,
        **kwargs,
    )
