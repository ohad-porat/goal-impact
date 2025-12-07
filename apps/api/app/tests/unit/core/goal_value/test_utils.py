"""Unit tests for goal value utility functions."""

from app.core.goal_value.utils import (
    MAX_MINUTE,
    MAX_SCORE_DIFF,
    MIN_MINUTE,
    MIN_SCORE_DIFF,
    calculate_outcome,
    calculate_window_bounds,
    get_minute_range,
    get_score_diff_range,
    get_scoring_team_id,
    validate_goal_data,
)


class TestCalculateOutcome:
    """Tests for calculate_outcome function."""

    def test_returns_win_when_scoring_team_wins(self) -> None:
        """Test that 'win' is returned when scoring team has higher final score."""
        assert calculate_outcome(2, 1) == "win"
        assert calculate_outcome(3, 0) == "win"
        assert calculate_outcome(5, 2) == "win"

    def test_returns_loss_when_scoring_team_loses(self) -> None:
        """Test that 'loss' is returned when scoring team has lower final score."""
        assert calculate_outcome(1, 2) == "loss"
        assert calculate_outcome(0, 3) == "loss"
        assert calculate_outcome(2, 5) == "loss"

    def test_returns_draw_when_scores_equal(self) -> None:
        """Test that 'draw' is returned when final scores are equal."""
        assert calculate_outcome(0, 0) == "draw"
        assert calculate_outcome(1, 1) == "draw"
        assert calculate_outcome(3, 3) == "draw"

    def test_handles_large_scores(self) -> None:
        """Test that function handles large score differences."""
        assert calculate_outcome(10, 0) == "win"
        assert calculate_outcome(0, 10) == "loss"
        assert calculate_outcome(100, 100) == "draw"

    def test_handles_zero_scores(self) -> None:
        """Test that function handles zero scores correctly."""
        assert calculate_outcome(0, 0) == "draw"
        assert calculate_outcome(1, 0) == "win"
        assert calculate_outcome(0, 1) == "loss"


class TestCalculateWindowBounds:
    """Tests for calculate_window_bounds function."""

    def test_normal_minute_with_default_window(self) -> None:
        """Test window calculation for normal minute with default window size."""
        window_start, window_end = calculate_window_bounds(45)
        assert window_start == 43
        assert window_end == 47

    def test_normal_minute_with_custom_window(self) -> None:
        """Test window calculation for normal minute with custom window size."""
        window_start, window_end = calculate_window_bounds(45, window_size=7)
        assert window_start == 42
        assert window_end == 48

    def test_lower_boundary_minute(self) -> None:
        """Test window calculation at minimum minute boundary."""
        window_start, window_end = calculate_window_bounds(MIN_MINUTE)
        assert window_start == MIN_MINUTE
        assert window_end == 3

    def test_upper_boundary_minute(self) -> None:
        """Test window calculation at maximum minute boundary."""
        window_start, window_end = calculate_window_bounds(MAX_MINUTE)
        assert window_start == 93
        assert window_end == MAX_MINUTE

    def test_minute_near_lower_boundary(self) -> None:
        """Test window calculation near minimum minute."""
        window_start, window_end = calculate_window_bounds(2)
        assert window_start == MIN_MINUTE
        assert window_end == 4

    def test_minute_near_upper_boundary(self) -> None:
        """Test window calculation near maximum minute."""
        window_start, window_end = calculate_window_bounds(94)
        assert window_start == 92
        assert window_end == MAX_MINUTE

    def test_minute_at_exact_boundary_with_window(self) -> None:
        """Test window calculation when minute is exactly at boundary after window calculation."""
        window_start, window_end = calculate_window_bounds(3)
        assert window_start == MIN_MINUTE
        assert window_end == 5

    def test_odd_window_size(self) -> None:
        """Test window calculation with odd window size."""
        window_start, window_end = calculate_window_bounds(50, window_size=5)
        assert window_start == 48
        assert window_end == 52

    def test_even_window_size(self) -> None:
        """Test window calculation with even window size (integer division)."""
        window_start, window_end = calculate_window_bounds(50, window_size=6)
        assert window_start == 47
        assert window_end == 53

    def test_large_window_size(self) -> None:
        """Test window calculation with large window size."""
        window_start, window_end = calculate_window_bounds(50, window_size=20)
        assert window_start == 40
        assert window_end == 60

    def test_window_size_larger_than_minute_range(self) -> None:
        """Test window calculation when window size exceeds minute range."""
        window_start, window_end = calculate_window_bounds(50, window_size=200)
        assert window_start == MIN_MINUTE
        assert window_end == MAX_MINUTE


class TestValidateGoalData:
    """Tests for validate_goal_data function."""

    def test_returns_true_for_valid_goal(self, mocker) -> None:
        """Test that valid goal data returns True."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is True

    def test_returns_false_when_home_pre_event_missing(self, mocker) -> None:
        """Test that goal with missing home_team_goals_pre_event returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = None
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is False

    def test_returns_false_when_away_pre_event_missing(self, mocker) -> None:
        """Test that goal with missing away_team_goals_pre_event returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = None
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is False

    def test_returns_false_when_home_post_event_missing(self, mocker) -> None:
        """Test that goal with missing home_team_goals_post_event returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = None
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is False

    def test_returns_false_when_away_post_event_missing(self, mocker) -> None:
        """Test that goal with missing away_team_goals_post_event returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = None
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is False

    def test_returns_false_when_match_home_goals_missing(self, mocker) -> None:
        """Test that goal with missing match.home_team_goals returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = None
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is False

    def test_returns_false_when_match_away_goals_missing(self, mocker) -> None:
        """Test that goal with missing match.away_team_goals returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = None

        assert validate_goal_data(goal) is False

    def test_returns_false_when_match_home_goals_not_integer(self, mocker) -> None:
        """Test that goal with non-integer match.home_team_goals returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2.5
        goal.match.away_team_goals = 1

        assert validate_goal_data(goal) is False

    def test_returns_false_when_match_away_goals_not_integer(self, mocker) -> None:
        """Test that goal with non-integer match.away_team_goals returns False."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 0
        goal.away_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_post_event = 0
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = "1"

        assert validate_goal_data(goal) is False

    def test_returns_true_with_all_valid_integer_values(self, mocker) -> None:
        """Test that goal with all valid integer values returns True."""
        goal = mocker.Mock()
        goal.home_team_goals_pre_event = 1
        goal.away_team_goals_pre_event = 2
        goal.home_team_goals_post_event = 2
        goal.away_team_goals_post_event = 2
        goal.match.home_team_goals = 3
        goal.match.away_team_goals = 2

        assert validate_goal_data(goal) is True


class TestGetScoreDiffRange:
    """Tests for get_score_diff_range function."""

    def test_returns_correct_range(self) -> None:
        """Test that function returns correct range of score differences."""
        score_diff_range = get_score_diff_range()
        assert isinstance(score_diff_range, range)
        assert score_diff_range.start == MIN_SCORE_DIFF
        assert score_diff_range.stop == MAX_SCORE_DIFF + 1
        assert list(score_diff_range) == list(range(MIN_SCORE_DIFF, MAX_SCORE_DIFF + 1))

    def test_range_includes_boundaries(self) -> None:
        """Test that range includes both MIN_SCORE_DIFF and MAX_SCORE_DIFF."""
        score_diff_range = list(get_score_diff_range())
        assert MIN_SCORE_DIFF in score_diff_range
        assert MAX_SCORE_DIFF in score_diff_range

    def test_range_has_correct_length(self) -> None:
        """Test that range has correct length."""
        score_diff_range = list(get_score_diff_range())
        expected_length = MAX_SCORE_DIFF - MIN_SCORE_DIFF + 1
        assert len(score_diff_range) == expected_length


class TestGetMinuteRange:
    """Tests for get_minute_range function."""

    def test_returns_correct_range(self) -> None:
        """Test that function returns correct range of minutes."""
        minute_range = get_minute_range()
        assert isinstance(minute_range, range)
        assert minute_range.start == MIN_MINUTE
        assert minute_range.stop == MAX_MINUTE + 1
        assert list(minute_range) == list(range(MIN_MINUTE, MAX_MINUTE + 1))

    def test_range_includes_boundaries(self) -> None:
        """Test that range includes both MIN_MINUTE and MAX_MINUTE."""
        minute_range = list(get_minute_range())
        assert MIN_MINUTE in minute_range
        assert MAX_MINUTE in minute_range

    def test_range_has_correct_length(self) -> None:
        """Test that range has correct length."""
        minute_range = list(get_minute_range())
        expected_length = MAX_MINUTE - MIN_MINUTE + 1
        assert len(minute_range) == expected_length


class TestGetScoringTeamId:
    """Tests for get_scoring_team_id function."""

    def test_returns_home_team_id_when_home_scored(self) -> None:
        """Test that function returns home_team_id when only home team scored."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=1,
            home_goals_pre=0,
            away_goals_post=0,
            away_goals_pre=0,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result == home_team_id

    def test_returns_away_team_id_when_away_scored(self) -> None:
        """Test that function returns away_team_id when only away team scored."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=0,
            home_goals_pre=0,
            away_goals_post=1,
            away_goals_pre=0,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result == away_team_id

    def test_returns_none_when_both_teams_scored(self) -> None:
        """Test that function returns None when both teams scored simultaneously."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=1,
            home_goals_pre=0,
            away_goals_post=1,
            away_goals_pre=0,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result is None

    def test_returns_none_when_neither_team_scored(self) -> None:
        """Test that function returns None when neither team scored."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=0,
            home_goals_pre=0,
            away_goals_post=0,
            away_goals_pre=0,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result is None

    def test_returns_none_when_goals_decreased(self) -> None:
        """Test that function returns None when goal counts decreased (invalid scenario)."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=0,
            home_goals_pre=1,
            away_goals_post=0,
            away_goals_pre=1,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result is None

    def test_handles_multiple_goals(self) -> None:
        """Test that function handles multiple goals correctly."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=3,
            home_goals_pre=1,
            away_goals_post=0,
            away_goals_pre=0,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result == home_team_id

    def test_handles_negative_goal_counts(self) -> None:
        """Test that function handles negative goal counts (edge case)."""
        home_team_id = 1
        away_team_id = 2
        result = get_scoring_team_id(
            home_goals_post=-1,
            home_goals_pre=0,
            away_goals_post=0,
            away_goals_pre=0,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        )
        assert result is None
