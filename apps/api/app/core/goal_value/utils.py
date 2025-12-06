"""Utility functions and constants for goal value calculations."""

MIN_SCORE_DIFF = -3
MAX_SCORE_DIFF = 5
MIN_MINUTE = 1
MAX_MINUTE = 95
DEFAULT_WINDOW_SIZE = 5
NOISE_THRESHOLD = -0.05


def calculate_outcome(scoring_team_final: int, opponent_final: int) -> str:
    """Calculate match outcome based on final scores.

    Args:
        scoring_team_final: Final score of the scoring team
        opponent_final: Final score of the opponent team

    Returns:
        "win", "loss", or "draw"
    """
    if scoring_team_final > opponent_final:
        return "win"
    elif scoring_team_final < opponent_final:
        return "loss"
    else:
        return "draw"


def calculate_window_bounds(minute: int, window_size: int = DEFAULT_WINDOW_SIZE) -> tuple[int, int]:
    """Calculate window start and end bounds for a given minute.

    Creates a symmetric window around the minute, clamped to valid minute range.

    Args:
        minute: Center minute for the window
        window_size: Size of the window (default: 5)

    Returns:
        Tuple of (window_start, window_end), clamped to [MIN_MINUTE, MAX_MINUTE]
    """
    window_start = max(MIN_MINUTE, minute - window_size // 2)
    window_end = min(MAX_MINUTE, minute + window_size // 2)
    return window_start, window_end


def validate_goal_data(goal) -> bool:
    """Validate that goal has all required data fields.

    Checks that all goal event scores and match final scores are present and valid.

    Args:
        goal: Goal event object with match relationship

    Returns:
        True if all required fields are present and valid, False otherwise
    """
    return (
        goal.home_team_goals_pre_event is not None
        and goal.away_team_goals_pre_event is not None
        and goal.home_team_goals_post_event is not None
        and goal.away_team_goals_post_event is not None
        and goal.match.home_team_goals is not None
        and goal.match.away_team_goals is not None
        and isinstance(goal.match.home_team_goals, int)
        and isinstance(goal.match.away_team_goals, int)
    )


def get_score_diff_range():
    """Get the range of score differences.

    Returns:
        Range from MIN_SCORE_DIFF to MAX_SCORE_DIFF (inclusive)
    """
    return range(MIN_SCORE_DIFF, MAX_SCORE_DIFF + 1)


def get_minute_range():
    """Get the range of minutes.

    Returns:
        Range from MIN_MINUTE to MAX_MINUTE (inclusive)
    """
    return range(MIN_MINUTE, MAX_MINUTE + 1)


def get_scoring_team_id(
    home_goals_post: int,
    home_goals_pre: int,
    away_goals_post: int,
    away_goals_pre: int,
    home_team_id: int,
    away_team_id: int,
) -> int | None:
    """Determine which team scored based on goal count changes.

    Args:
        home_goals_post: Home team goals after the event
        home_goals_pre: Home team goals before the event
        away_goals_post: Away team goals after the event
        away_goals_pre: Away team goals before the event
        home_team_id: ID of the home team
        away_team_id: ID of the away team

    Returns:
        Team ID that scored, or None if unclear (both teams scored or neither)
    """
    home_scored = home_goals_post > home_goals_pre
    away_scored = away_goals_post > away_goals_pre

    if home_scored and not away_scored:
        return home_team_id
    elif away_scored and not home_scored:
        return away_team_id

    return None
