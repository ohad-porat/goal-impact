"""Shared test helpers for creating test data."""

from datetime import date

from fastapi.testclient import TestClient

from app.tests.utils.factories import (
    CompetitionFactory,
    EventFactory,
    MatchFactory,
    NationFactory,
    PlayerFactory,
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


def assert_404_not_found(client: TestClient, url: str, resource_name: str = None):
    """Assert that a GET request returns 404 with appropriate error message."""
    response = client.get(url)
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
    if resource_name:
        assert resource_name.lower() in data["detail"].lower()


def assert_422_validation_error(client: TestClient, url: str):
    """Assert that a GET request with invalid ID type returns 422 validation error."""
    response = client.get(url)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


# Invalid ID values used for testing validation
INVALID_ID_VALUES = ["not-a-number", "abc", "12.5"]


def assert_invalid_id_types_return_422(
    client: TestClient, url_template: str, id_placeholder: str = "{invalid_id}"
):
    """Assert that various invalid ID types return 422 validation error.
    
    Args:
        client: FastAPI TestClient instance
        url_template: URL template with placeholder for invalid ID (e.g., "/api/v1/players/{invalid_id}")
        id_placeholder: The placeholder string to replace (default: "{invalid_id}")
    
    Examples:
        # Path parameter
        assert_invalid_id_types_return_422(client, "/api/v1/players/{invalid_id}")
        
        # Query parameter
        assert_invalid_id_types_return_422(client, "/api/v1/home/recent-goals?league_id={invalid_id}")
    """
    for invalid_id in INVALID_ID_VALUES:
        url = url_template.replace(id_placeholder, invalid_id)
        assert_422_validation_error(client, url)


def assert_empty_list_response(client: TestClient, url: str, list_field_name: str):
    """Assert that a GET request returns 200 with an empty list."""
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data[list_field_name] == []


def create_match_with_goal(
    db_session,
    goal_value=5.5,
    minute=45,
    with_assist=False,
    match_date=None,
    home_pre=0,
    home_post=1,
    away_pre=0,
    away_post=0,
    home_team_name=None,
    away_team_name=None,
    event_type="goal",
    xg=None,
    post_shot_xg=None,
):
    """Create a match with a goal event, optionally with assist."""
    nation, comp, season = create_basic_season_setup(db_session)
    team = (
        TeamFactory(name=home_team_name, nation=nation)
        if home_team_name
        else TeamFactory(nation=nation)
    )
    opponent = (
        TeamFactory(name=away_team_name, nation=nation)
        if away_team_name
        else TeamFactory(nation=nation)
    )
    player = PlayerFactory(nation=nation)

    if match_date is None:
        match_date = date.today()

    match = MatchFactory(season=season, home_team=team, away_team=opponent, date=match_date)

    assister = None
    if with_assist:
        assister = PlayerFactory(nation=nation)
        create_assist_event(match, assister, minute, home_pre, home_post, away_pre, away_post)

    create_goal_event(
        match,
        player,
        minute,
        home_pre,
        home_post,
        away_pre,
        away_post,
        goal_value=goal_value,
        event_type=event_type,
        xg=xg,
        post_shot_xg=post_shot_xg,
    )
    db_session.commit()
    return match, player, team, season, assister


def create_two_competitions_with_data(db_session, create_data_func, start_year=2023, end_year=2024):
    """Create two competitions with data for testing league_id filtering."""
    nation = NationFactory()
    comp1 = CompetitionFactory(name="Premier League", nation=nation)
    comp2 = CompetitionFactory(name="Championship", nation=nation)
    season1 = SeasonFactory(competition=comp1, start_year=start_year, end_year=end_year)
    season2 = SeasonFactory(competition=comp2, start_year=start_year, end_year=end_year)

    data1 = create_data_func(season1, nation)
    data2 = create_data_func(season2, nation)
    db_session.commit()
    return comp1, comp2, data1, data2, nation


def create_mock_session_with_queries(mocker, player_stats, events):
    """Return a configured mock session with query side effects for testing PlayerStatsGoalValueUpdater."""
    mock_query1 = mocker.Mock()
    mock_query1.all.return_value = player_stats

    mock_query2 = mocker.Mock()
    mock_query2.join.return_value.filter.return_value.all.return_value = events

    def query_side_effect(*args):
        if len(args) == 1 and hasattr(args[0], "__name__") and args[0].__name__ == "PlayerStats":
            return mock_query1
        return mock_query2

    session = mocker.Mock()
    session.query.side_effect = query_side_effect
    return session
