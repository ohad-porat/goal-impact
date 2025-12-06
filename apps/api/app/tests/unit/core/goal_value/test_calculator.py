"""Unit tests for goal value calculator."""

from collections import defaultdict

import pytest

from app.core.goal_value.calculator import GoalValueCalculator
from app.core.goal_value.utils import MAX_MINUTE, MIN_MINUTE, MIN_SCORE_DIFF, NOISE_THRESHOLD

FLOAT_TOLERANCE = 0.0001


class TestInit:
    """Tests for __init__ method."""

    def test_initializes_with_dependencies(self, mocker):
        """Test that calculator initializes with data processor and repository."""
        mocker.patch("app.core.goal_value.calculator.GoalDataProcessor")
        mocker.patch("app.core.goal_value.calculator.GoalValueRepository")
        
        calculator = GoalValueCalculator()

        assert calculator.data_processor is not None
        assert calculator.repository is not None
        assert isinstance(calculator.goal_value_dict, defaultdict)
        assert len(calculator.goal_value_dict) == 0


class TestGetCalculationWindow:
    """Tests for _get_calculation_window method."""

    @pytest.mark.parametrize("minute,expected_start,expected_end", [
        (45, 43, 47),
        (MIN_MINUTE, MIN_MINUTE, 3),
        (MAX_MINUTE, 93, MAX_MINUTE),
        (2, MIN_MINUTE, 4),
        (94, 92, MAX_MINUTE),
    ])
    def test_returns_window_for_minute(self, minute, expected_start, expected_end):
        """Test that method returns correct window for various minutes."""
        calculator = GoalValueCalculator()
        window_start, window_end = calculator._get_calculation_window(minute)

        assert window_start == expected_start
        assert window_end == expected_end


class TestCalculateGoalValueForScoreDiff:
    """Tests for _calculate_goal_value_for_score_diff method."""

    def test_calculates_pure_win(self):
        """Test that method calculates correctly for pure win scenario."""
        calculator = GoalValueCalculator()
        score_diff_data = {"win": 10, "draw": 0, "loss": 0, "total": 10}

        result = calculator._calculate_goal_value_for_score_diff(score_diff_data)

        assert result == 1.0

    def test_calculates_pure_loss(self):
        """Test that method calculates correctly for pure loss scenario."""
        calculator = GoalValueCalculator()
        score_diff_data = {"win": 0, "draw": 0, "loss": 10, "total": 10}

        result = calculator._calculate_goal_value_for_score_diff(score_diff_data)

        assert result == 0.0

    def test_calculates_pure_draw(self):
        """Test that method calculates correctly for pure draw scenario."""
        calculator = GoalValueCalculator()
        score_diff_data = {"win": 0, "draw": 9, "loss": 0, "total": 9}

        result = calculator._calculate_goal_value_for_score_diff(score_diff_data)

        assert abs(result - (1 / 3)) < FLOAT_TOLERANCE

    def test_calculates_mixed_outcomes(self):
        """Test that method calculates correctly for mixed outcomes."""
        calculator = GoalValueCalculator()
        score_diff_data = {"win": 6, "draw": 3, "loss": 1, "total": 10}

        result = calculator._calculate_goal_value_for_score_diff(score_diff_data)

        expected = (6 + 3 / 3) / 10
        assert abs(result - expected) < FLOAT_TOLERANCE

    def test_handles_small_totals(self):
        """Test that method handles small total values correctly."""
        calculator = GoalValueCalculator()
        score_diff_data = {"win": 1, "draw": 1, "loss": 0, "total": 2}

        result = calculator._calculate_goal_value_for_score_diff(score_diff_data)

        expected = (1 + 1 / 3) / 2
        assert abs(result - expected) < FLOAT_TOLERANCE


class TestCalculateGoalValue:
    """Tests for _calculate_goal_value method."""

    def test_calculates_goal_value_for_single_minute_score_diff(self, mocker):
        """Test that method calculates goal value for single minute and score_diff."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator._calculate_goal_value(aggregated_data)

        assert 45 in calculator.goal_value_dict
        assert 1 in calculator.goal_value_dict[45]
        expected = (6 + 3 / 3) / 10
        assert abs(calculator.goal_value_dict[45][1] - round(expected, 3)) < FLOAT_TOLERANCE

    def test_uses_window_data_for_calculation(self, mocker):
        """Test that method uses window data for calculation."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 2, "draw": 1, "loss": 1, "total": 4},
        }

        window_data = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.data_processor.get_window_data.return_value = window_data

        calculator._calculate_goal_value(aggregated_data)

        calculator.data_processor.get_window_data.assert_called_once()
        call_args = calculator.data_processor.get_window_data.call_args
        assert call_args[0][0] == aggregated_data
        assert call_args[0][1] == 43
        assert call_args[0][2] == 47

    def test_skips_minutes_without_data(self, mocker):
        """Test that method skips minutes without data."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator._calculate_goal_value(aggregated_data)

        assert 45 in calculator.goal_value_dict
        assert 50 not in calculator.goal_value_dict

    def test_skips_score_diffs_without_data(self, mocker):
        """Test that method skips score_diffs without data."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
            0: {"win": 0, "draw": 0, "loss": 0, "total": 0},
        }

        calculator._calculate_goal_value(aggregated_data)

        assert 1 in calculator.goal_value_dict[45]
        assert 0 not in calculator.goal_value_dict[45]

    def test_handles_empty_aggregated_data(self, mocker):
        """Test that method handles empty aggregated_data gracefully."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()
        calculator._enforce_minimal_monotonicity = mocker.Mock()

        calculator._calculate_goal_value({})

        calculator._enforce_minimal_monotonicity.assert_called_once()
        assert len(calculator.goal_value_dict) == 0
        calculator.data_processor.get_window_data.assert_not_called()

    def test_rounds_goal_value_to_three_decimals(self, mocker):
        """Test that method rounds goal value to three decimal places."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 1, "draw": 1, "loss": 0, "total": 2},
        }

        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 1, "draw": 1, "loss": 0, "total": 2},
        }

        calculator._calculate_goal_value(aggregated_data)

        goal_value = calculator.goal_value_dict[45][1]
        assert isinstance(goal_value, float)
        assert goal_value == round(goal_value, 3)

    def test_calls_enforce_monotonicity(self, mocker):
        """Test that method calls _enforce_minimal_monotonicity at the end."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()
        calculator._enforce_minimal_monotonicity = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator._calculate_goal_value(aggregated_data)

        calculator._enforce_minimal_monotonicity.assert_called_once()

    def test_handles_multiple_minutes_and_score_diffs(self, mocker):
        """Test that method handles multiple minutes and score_diffs."""
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()

        aggregated_data = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
            (45, 0): {"win": 2, "draw": 4, "loss": 2, "total": 8},
            (90, 1): {"win": 8, "draw": 1, "loss": 1, "total": 10},
        }

        def get_window_data_side_effect(agg_data, start, end):
            if start == 43 and end == 47:
                return {
                    1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
                    0: {"win": 2, "draw": 4, "loss": 2, "total": 8},
                }
            elif start == 88 and end == 92:
                return {
                    1: {"win": 8, "draw": 1, "loss": 1, "total": 10},
                }
            return {}

        calculator.data_processor.get_window_data.side_effect = get_window_data_side_effect

        calculator._calculate_goal_value(aggregated_data)

        assert 45 in calculator.goal_value_dict
        assert 90 in calculator.goal_value_dict
        assert 1 in calculator.goal_value_dict[45]
        assert 0 in calculator.goal_value_dict[45]
        assert 1 in calculator.goal_value_dict[90]


class TestEnforceMinimalMonotonicity:
    """Tests for _enforce_minimal_monotonicity method."""

    def test_fixes_small_negative_margin(self):
        """Test that method fixes small negative margins within noise threshold."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {1: 0.6, 2: 0.58},
        }

        calculator._enforce_minimal_monotonicity()

        assert calculator.goal_value_dict[45][2] == 0.6

    def test_does_not_fix_large_negative_margin(self):
        """Test that method does not fix large negative margins."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {1: 0.6, 2: 0.4},
        }

        calculator._enforce_minimal_monotonicity()

        assert calculator.goal_value_dict[45][2] == 0.4

    def test_does_not_fix_positive_margin(self):
        """Test that method does not fix positive margins."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {1: 0.5, 2: 0.6},
        }

        calculator._enforce_minimal_monotonicity()

        assert calculator.goal_value_dict[45][1] == 0.5
        assert calculator.goal_value_dict[45][2] == 0.6

    def test_handles_missing_values(self):
        """Test that method handles missing values correctly."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {1: 0.6},
        }

        calculator._enforce_minimal_monotonicity()

        assert calculator.goal_value_dict[45][1] == 0.6

    def test_handles_none_values(self):
        """Test that method handles None values correctly."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {1: None, 2: 0.6},
        }

        calculator._enforce_minimal_monotonicity()

        assert calculator.goal_value_dict[45][1] is None
        assert calculator.goal_value_dict[45][2] == 0.6

    def test_handles_multiple_minutes(self):
        """Test that method handles multiple minutes correctly."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {1: 0.6, 2: 0.58},
            90: {1: 0.5, 2: 0.48},
        }

        calculator._enforce_minimal_monotonicity()

        assert calculator.goal_value_dict[45][2] == 0.6
        assert calculator.goal_value_dict[90][2] == 0.5

    def test_handles_boundary_score_diffs(self):
        """Test that method handles boundary score_diffs correctly."""
        calculator = GoalValueCalculator()
        calculator.goal_value_dict = {
            45: {MIN_SCORE_DIFF: 0.2, MIN_SCORE_DIFF + 1: 0.18},
        }

        calculator._enforce_minimal_monotonicity()

        margin = (
            calculator.goal_value_dict[45][MIN_SCORE_DIFF + 1]
            - calculator.goal_value_dict[45][MIN_SCORE_DIFF]
        )
        assert margin == 0.0
        assert (
            calculator.goal_value_dict[45][MIN_SCORE_DIFF + 1]
            == calculator.goal_value_dict[45][MIN_SCORE_DIFF]
        )


class TestRun:
    """Tests for run method."""

    def test_runs_full_calculation_flow(self, mocker):
        """Test that run method executes full calculation flow."""
        mocker.patch("builtins.print")
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()
        calculator.repository = mocker.Mock()

        mock_goals = [mocker.Mock(), mocker.Mock()]
        calculator.data_processor.query_goals.return_value = mock_goals

        aggregated_data = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }
        calculator.data_processor.process_goal_data.return_value = aggregated_data

        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.run()

        calculator.data_processor.query_goals.assert_called_once()
        calculator.data_processor.process_goal_data.assert_called_once_with(mock_goals)
        calculator.repository.persist_goal_values.assert_called_once()
        calculator.repository.save_metadata.assert_called_once_with(2)

    def test_handles_empty_goals(self, mocker):
        """Test that run method handles empty goals list."""
        mocker.patch("builtins.print")
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()
        calculator.repository = mocker.Mock()

        calculator.data_processor.query_goals.return_value = []
        calculator.data_processor.process_goal_data.return_value = {}

        calculator.run()

        calculator.repository.persist_goal_values.assert_called_once()
        calculator.repository.save_metadata.assert_called_once_with(0)

    def test_prints_progress_messages(self, mocker):
        """Test that run method prints progress messages."""
        mock_print = mocker.patch("builtins.print")
        calculator = GoalValueCalculator()
        calculator.data_processor = mocker.Mock()
        calculator.repository = mocker.Mock()

        calculator.data_processor.query_goals.return_value = [mocker.Mock()]
        calculator.data_processor.process_goal_data.return_value = {
            (45, 1): {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }
        calculator.data_processor.get_window_data.return_value = {
            1: {"win": 6, "draw": 3, "loss": 1, "total": 10},
        }

        calculator.run()

        assert mock_print.call_count >= 5
        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Starting goal value calculation" in print_output
        assert "Found" in print_output and "goals" in print_output
        assert "completed successfully" in print_output
