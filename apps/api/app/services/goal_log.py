"""Goal log related services - reusable for teams and players."""

from datetime import date

from app.models.events import Event
from app.models.matches import Match
from app.models.players import Player
from app.models.teams import Team
from app.schemas.clubs import GoalLogEntry, PlayerBasic, PlayerGoalLogEntry
from app.services.common import build_club_info


def is_goal_for_team(goal_event: Event, match: Match, team_id: int) -> bool:
    """Determine if a goal was scored FOR the specified team.

    Args:
        goal_event: The Event object representing the goal
        match: The Match object containing the goal event
        team_id: The ID of the team to check

    Returns:
        True if the goal was scored for the specified team, False otherwise
    """
    if (
        goal_event.home_team_goals_post_event is None
        or goal_event.home_team_goals_pre_event is None
    ):
        return False

    home_scored = goal_event.home_team_goals_post_event > goal_event.home_team_goals_pre_event

    if home_scored and match.home_team_id == team_id:
        return True
    elif not home_scored and match.away_team_id == team_id:
        return True
    return False


def format_score(goal_event: Event) -> tuple[str, str]:
    """Format score before and after the goal.

    Args:
        goal_event: The Event object representing the goal

    Returns:
        Tuple of (score_before, score_after) as formatted strings (e.g., "1-0")
        Returns ("", "") if score data is incomplete
    """
    if (
        goal_event.home_team_goals_pre_event is None
        or goal_event.away_team_goals_pre_event is None
        or goal_event.home_team_goals_post_event is None
        or goal_event.away_team_goals_post_event is None
    ):
        return "", ""

    score_before = f"{goal_event.home_team_goals_pre_event}-{goal_event.away_team_goals_pre_event}"
    score_after = f"{goal_event.home_team_goals_post_event}-{goal_event.away_team_goals_post_event}"
    return score_before, score_after


def get_assist_for_goal_from_data(
    assist_event: Event | None, assist_player: Player | None
) -> PlayerBasic | None:
    """Get the assisting player for a goal from pre-loaded data."""
    if not assist_event or not assist_player:
        return None

    return PlayerBasic(id=assist_player.id, name=assist_player.name)


def format_scorer_name(scorer: Player, event_type: str) -> str:
    """Format scorer name, adding (OG) for own goals."""
    if event_type == "own goal":
        return f"{scorer.name} (OG)"
    return scorer.name


def get_venue_for_team(match: Match, team_id: int) -> str:
    """Get venue (Home/Away) for a team in a match.

    Args:
        match: The Match object
        team_id: The ID of the team to check

    Returns:
        "Home" if the team is the home team, "Away" otherwise
    """
    return "Home" if match.home_team_id == team_id else "Away"


def build_team_season_goal_log_entry_from_data(
    goal_event: Event,
    match: Match,
    scorer: Player,
    team_id: int,
    opponent_team: Team | None,
    assist_event: Event | None = None,
    assist_player: Player | None = None,
) -> GoalLogEntry | None:
    """Build a GoalLogEntry from pre-loaded data for a team/season."""
    if not is_goal_for_team(goal_event, match, team_id):
        return None

    if not opponent_team:
        return None

    venue = get_venue_for_team(match, team_id)
    score_before, score_after = format_score(goal_event)
    assisted_by = get_assist_for_goal_from_data(assist_event, assist_player)
    scorer_name = format_scorer_name(scorer, goal_event.event_type)

    return GoalLogEntry(
        date="",
        venue=venue,
        scorer=PlayerBasic(id=scorer.id, name=scorer_name),
        opponent=build_club_info(opponent_team),
        minute=goal_event.minute,
        score_before=score_before,
        score_after=score_after,
        goal_value=goal_event.goal_value,
        xg=goal_event.xg,
        post_shot_xg=goal_event.post_shot_xg,
        assisted_by=assisted_by,
    )


def _format_date(date_obj: date | None) -> str:
    """Format date object to string."""
    return date_obj.strftime("%d/%m/%Y") if date_obj else ""


def sort_and_format_team_season_goal_entries(
    goal_entries_with_date: list[tuple[date | None, GoalLogEntry]],
) -> list[GoalLogEntry]:
    """Sort team season goal entries by date and minute, then format dates.

    Entries with None dates are sorted last (using date.max as sentinel).

    Args:
        goal_entries_with_date: List of tuples containing (date, GoalLogEntry)

    Returns:
        Sorted list of GoalLogEntry objects with formatted dates
    """
    # Use date.max as sentinel for None dates to ensure they sort last
    goal_entries_with_date.sort(key=lambda g: (g[0] if g[0] is not None else date.max, g[1].minute))

    goal_entries = []
    for date_obj, goal_entry in goal_entries_with_date:
        goal_entry.date = _format_date(date_obj)
        goal_entries.append(goal_entry)

    return goal_entries


def sort_and_format_player_career_goal_entries(
    goal_entries_with_date_season: list[tuple[date | None, int | None, PlayerGoalLogEntry]],
) -> list[PlayerGoalLogEntry]:
    """Sort player career goal entries by season, date and minute, then format dates."""
    goal_entries_with_date_season.sort(
        key=lambda g: (
            g[1] if g[1] is not None else 0,
            g[0] if g[0] is not None else "",
            g[2].minute,
        )
    )

    goal_entries = []
    for date_obj, _, goal_entry in goal_entries_with_date_season:
        goal_entry.date = _format_date(date_obj)
        goal_entries.append(goal_entry)

    return goal_entries


def build_player_career_goal_log_entry_from_data(
    goal_event: Event,
    match: Match,
    scorer: Player,
    season_display_name: str,
    player_team: Team | None,
    opponent_team: Team | None,
    assist_event: Event | None = None,
    assist_player: Player | None = None,
) -> PlayerGoalLogEntry | None:
    """Build a PlayerGoalLogEntry from pre-loaded data for a player/career."""
    if not player_team or not opponent_team:
        return None

    venue = get_venue_for_team(match, player_team.id)
    score_before, score_after = format_score(goal_event)
    assisted_by = get_assist_for_goal_from_data(assist_event, assist_player)

    return PlayerGoalLogEntry(
        date="",
        venue=venue,
        team=build_club_info(player_team),
        opponent=build_club_info(opponent_team),
        minute=goal_event.minute,
        score_before=score_before,
        score_after=score_after,
        goal_value=goal_event.goal_value,
        xg=goal_event.xg,
        post_shot_xg=goal_event.post_shot_xg,
        assisted_by=assisted_by,
        season_id=match.season_id,
        season_display_name=season_display_name,
    )
