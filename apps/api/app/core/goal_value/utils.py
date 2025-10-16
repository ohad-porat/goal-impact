"""Utility functions and constants for goal value calculations."""

from typing import Tuple


MIN_SCORE_DIFF = -3
MAX_SCORE_DIFF = 5
MIN_MINUTE = 1
MAX_MINUTE = 95
DEFAULT_WINDOW_SIZE = 5
NOISE_THRESHOLD = -0.05


def calculate_outcome(scoring_team_final: int, opponent_final: int) -> str:
    """Calculate match outcome based on final scores."""
    if scoring_team_final > opponent_final:
        return "win"
    elif scoring_team_final < opponent_final:
        return "loss"
    else:
        return "draw"


def calculate_window_bounds(minute: int, window_size: int = DEFAULT_WINDOW_SIZE) -> Tuple[int, int]:
    """Calculate window start and end bounds for a given minute."""
    window_start = max(MIN_MINUTE, minute - window_size // 2)
    window_end = min(MAX_MINUTE, minute + window_size // 2)
    return window_start, window_end


def validate_goal_data(goal) -> bool:
    """Validate that goal has all required data fields."""
    return (
        goal.home_team_goals_pre_event is not None and
        goal.away_team_goals_pre_event is not None and
        goal.home_team_goals_post_event is not None and
        goal.away_team_goals_post_event is not None and
        goal.match.home_team_goals is not None and
        goal.match.away_team_goals is not None and
        isinstance(goal.match.home_team_goals, int) and
        isinstance(goal.match.away_team_goals, int)
    )


def get_score_diff_range():
    """Get the range of score differences."""
    return range(MIN_SCORE_DIFF, MAX_SCORE_DIFF + 1)


def get_minute_range():
    """Get the range of minutes."""
    return range(MIN_MINUTE, MAX_MINUTE + 1)
