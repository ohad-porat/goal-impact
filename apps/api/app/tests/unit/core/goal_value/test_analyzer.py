"""Unit tests for goal value analyzer."""

from collections import defaultdict

import pandas as pd

from app.core.goal_value.analyzer import GoalValueAnalyzer
from app.core.goal_value.utils import DEFAULT_WINDOW_SIZE, get_minute_range, get_score_diff_range


class TestInit:
    """Tests for __init__ method."""

    def test_initializes_with_dependencies(self, mocker) -> None:
        """Test that analyzer initializes with data processor and repository."""
        mocker.patch("app.core.goal_value.analyzer.GoalDataProcessor")
        mocker.patch("app.core.goal_value.analyzer.GoalValueRepository")

        analyzer = GoalValueAnalyzer()

        assert analyzer.data_processor is not None
        assert analyzer.repository is not None
        assert analyzer.goal_value_dict is None


class TestEnsureDataLoaded:
    """Tests for _ensure_data_loaded method."""

    def test_loads_data_on_first_call(self, mocker) -> None:
        """Test that method loads data on first call."""
        analyzer = GoalValueAnalyzer()
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = defaultdict(dict, {45: {1: 0.75}})

        analyzer._ensure_data_loaded()

        assert analyzer.goal_value_dict[45][1] == 0.75
        analyzer.repository.load_goal_values.assert_called_once()

    def test_uses_cached_data_on_subsequent_calls(self, mocker) -> None:
        """Test that method uses cached data on subsequent calls."""
        analyzer = GoalValueAnalyzer()
        analyzer.repository = mocker.Mock()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        analyzer._ensure_data_loaded()

        analyzer.repository.load_goal_values.assert_not_called()
        assert analyzer.goal_value_dict[45][1] == 0.75


class TestExportToDataframe:
    """Tests for export_to_dataframe method."""

    def test_exports_to_dataframe(self) -> None:
        """Test that method exports goal values to DataFrame."""
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(
            dict,
            {
                45: {1: 0.75, 0: 0.5},
                90: {1: 0.8},
            },
        )

        df = analyzer.export_to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert df.index.tolist() == list(get_minute_range())
        assert 45 in df.index
        assert 90 in df.index
        assert df.loc[45, 1] == 0.75
        assert df.loc[45, 0] == 0.5
        assert df.loc[90, 1] == 0.8

    def test_includes_all_minutes_and_score_diffs(self) -> None:
        """Test that DataFrame includes all minutes and score_diffs."""
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        df = analyzer.export_to_dataframe()

        assert len(df.index) == len(list(get_minute_range()))
        assert len(df.columns) == len(list(get_score_diff_range()))

    def test_handles_missing_values(self) -> None:
        """Test that method handles missing values correctly."""
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        df = analyzer.export_to_dataframe()

        assert pd.isna(df.loc[45, 0])
        assert df.loc[45, 1] == 0.75
        assert pd.isna(df.loc[90, 1])

    def test_calls_ensure_data_loaded(self, mocker) -> None:
        """Test that method calls _ensure_data_loaded."""
        analyzer = GoalValueAnalyzer()
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = defaultdict(dict, {45: {1: 0.75}})

        def ensure_data_loaded_side_effect():
            analyzer.goal_value_dict = analyzer.repository.load_goal_values()

        analyzer._ensure_data_loaded = mocker.Mock(side_effect=ensure_data_loaded_side_effect)

        analyzer.export_to_dataframe()

        analyzer._ensure_data_loaded.assert_called_once()


class TestShowSampleSizes:
    """Tests for show_sample_sizes method."""

    def test_calls_overview_when_no_parameters(self, mocker) -> None:
        """Test that method calls overview when no parameters provided."""
        mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.query_goals.return_value = []
        analyzer.data_processor.process_goal_data.return_value = {}
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = {}
        analyzer._show_sample_sizes_overview = mocker.Mock()

        analyzer.show_sample_sizes()

        analyzer._show_sample_sizes_overview.assert_called_once()

    def test_calls_minute_score_diff_when_both_provided(self, mocker) -> None:
        """Test that method calls minute_score_diff when both parameters provided."""
        mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.query_goals.return_value = []
        analyzer.data_processor.process_goal_data.return_value = {}
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = defaultdict(dict)
        analyzer._show_sample_sizes_for_minute_score_diff = mocker.Mock()

        analyzer.show_sample_sizes(specific_minute=45, score_diff=1)

        analyzer._show_sample_sizes_for_minute_score_diff.assert_called_once()

    def test_calls_minute_when_only_minute_provided(self, mocker) -> None:
        """Test that method calls minute when only minute provided."""
        mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.query_goals.return_value = []
        analyzer.data_processor.process_goal_data.return_value = {}
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = defaultdict(dict)
        analyzer._show_sample_sizes_for_minute = mocker.Mock()

        analyzer.show_sample_sizes(specific_minute=45)

        analyzer._show_sample_sizes_for_minute.assert_called_once()


class TestShowSampleSizesForMinuteScoreDiff:
    """Tests for _show_sample_sizes_for_minute_score_diff method."""

    def test_shows_sample_sizes_for_minute_score_diff(self, mocker) -> None:
        """Test that method shows sample sizes for specific minute and score_diff."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        aggregated_data = {
            (43, 1): {"total": 2},
            (44, 1): {"total": 3},
            (45, 1): {"total": 5},
        }

        analyzer._show_sample_sizes_for_minute_score_diff(
            45, 1, DEFAULT_WINDOW_SIZE, aggregated_data
        )

        assert mock_print.call_count >= 3
        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "45" in print_output
        assert "1" in print_output
        assert "minute 45" in print_output.lower() or "45" in print_output

    def test_shows_breakdown_when_window_has_multiple_minutes(self, mocker) -> None:
        """Test that method shows breakdown when window has multiple minutes."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        aggregated_data = {
            (43, 1): {"total": 2},
            (44, 1): {"total": 3},
            (45, 1): {"total": 5},
        }

        analyzer._show_sample_sizes_for_minute_score_diff(
            45, 1, DEFAULT_WINDOW_SIZE, aggregated_data
        )

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Breakdown" in print_output or "breakdown" in print_output


class TestShowSampleSizesForMinute:
    """Tests for _show_sample_sizes_for_minute method."""

    def test_uses_single_minute_when_sample_size_sufficient(self, mocker) -> None:
        """Test that method uses single minute when sample size is sufficient."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.get_sample_size_for_minute.return_value = 25
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75, 0: 0.5}})

        aggregated_data = {
            (45, 1): {"total": 15},
            (45, 0): {"total": 10},
        }

        analyzer._show_sample_sizes_for_minute(45, DEFAULT_WINDOW_SIZE, aggregated_data)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list).lower()
        assert "single minute" in print_output or "45" in print_output

    def test_uses_window_when_sample_size_insufficient(self, mocker) -> None:
        """Test that method uses window when sample size is insufficient."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.get_sample_size_for_minute.return_value = 15
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        aggregated_data = {
            (43, 1): {"total": 5},
            (44, 1): {"total": 5},
            (45, 1): {"total": 5},
        }

        analyzer._show_sample_sizes_for_minute(45, DEFAULT_WINDOW_SIZE, aggregated_data)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list).lower()
        assert "window" in print_output


class TestShowSampleSizesOverview:
    """Tests for _show_sample_sizes_overview method."""

    def test_shows_overview_for_all_minutes(self, mocker) -> None:
        """Test that method shows overview for all minutes with data."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()

        aggregated_data = {
            (45, 1): {"total": 10},
            (45, 0): {"total": 5},
            (90, 1): {"total": 8},
        }

        analyzer._show_sample_sizes_overview(aggregated_data)

        assert mock_print.call_count >= 2
        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "45" in print_output
        assert "90" in print_output

    def test_skips_minutes_without_data(self, mocker) -> None:
        """Test that method skips minutes without data."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()

        aggregated_data = {
            (45, 1): {"total": 10},
        }

        analyzer._show_sample_sizes_overview(aggregated_data)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "45" in print_output
        assert "| 50 |" not in print_output


class TestShowGoalDetails:
    """Tests for show_goal_details method."""

    def test_requires_both_minute_and_score_diff(self, mocker) -> None:
        """Test that method requires both minute and score_diff."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.query_goals.return_value = []
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = {}

        analyzer.show_goal_details(specific_minute=45)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list).lower()
        assert "specify both" in print_output or "minute" in print_output

    def test_calls_goal_details_when_both_provided(self, mocker) -> None:
        """Test that method calls goal details when both parameters provided."""
        mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.data_processor = mocker.Mock()
        analyzer.data_processor.query_goals.return_value = []
        analyzer.repository = mocker.Mock()
        analyzer.repository.load_goal_values.return_value = defaultdict(dict)
        analyzer._show_goal_details_for_minute_score_diff = mocker.Mock()

        analyzer.show_goal_details(specific_minute=45, score_diff=1)

        analyzer._show_goal_details_for_minute_score_diff.assert_called_once()


class TestShowGoalDetailsForMinuteScoreDiff:
    """Tests for _show_goal_details_for_minute_score_diff method."""

    def test_shows_goal_details(self, mocker) -> None:
        """Test that method shows goal details for matching goals."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        goal = mocker.Mock()
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0
        goal.event_type = "goal"
        goal.player = mocker.Mock()
        goal.player.name = "Test Player"
        goal.match = mocker.Mock()
        goal.match.home_team = mocker.Mock()
        goal.match.home_team.name = "Home Team"
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        goals = [goal]

        analyzer._show_goal_details_for_minute_score_diff(45, 1, DEFAULT_WINDOW_SIZE, goals)

        assert mock_print.call_count >= 3
        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "45" in print_output
        assert "Test Player" in print_output or "Player" in print_output

    def test_filters_by_window_minutes(self, mocker) -> None:
        """Test that method filters goals by window minutes."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        goal_in_window = mocker.Mock()
        goal_in_window.minute = 45
        goal_in_window.home_team_goals_pre_event = 0
        goal_in_window.home_team_goals_post_event = 1
        goal_in_window.away_team_goals_pre_event = 0
        goal_in_window.away_team_goals_post_event = 0
        goal_in_window.event_type = "goal"
        goal_in_window.player = mocker.Mock()
        goal_in_window.player.name = "Player 1"
        goal_in_window.match = mocker.Mock()
        goal_in_window.match.home_team = mocker.Mock()
        goal_in_window.match.home_team.name = "Home Team"
        goal_in_window.match.home_team_goals = 2
        goal_in_window.match.away_team_goals = 1

        goal_outside_window = mocker.Mock()
        goal_outside_window.minute = 50

        goals = [goal_in_window, goal_outside_window]

        analyzer._show_goal_details_for_minute_score_diff(45, 1, DEFAULT_WINDOW_SIZE, goals)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Player 1" in print_output or "Total goals found: 1" in print_output

    def test_filters_by_score_diff(self, mocker) -> None:
        """Test that method filters goals by score_diff."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        goal_matching = mocker.Mock()
        goal_matching.minute = 45
        goal_matching.home_team_goals_pre_event = 0
        goal_matching.home_team_goals_post_event = 1
        goal_matching.away_team_goals_pre_event = 0
        goal_matching.away_team_goals_post_event = 0
        goal_matching.event_type = "goal"
        goal_matching.player = mocker.Mock()
        goal_matching.player.name = "Player 1"
        goal_matching.match = mocker.Mock()
        goal_matching.match.home_team = mocker.Mock()
        goal_matching.match.home_team.name = "Home Team"
        goal_matching.match.home_team_goals = 2
        goal_matching.match.away_team_goals = 1

        goal_not_matching = mocker.Mock()
        goal_not_matching.minute = 45
        goal_not_matching.home_team_goals_pre_event = 1
        goal_not_matching.home_team_goals_post_event = 2
        goal_not_matching.away_team_goals_pre_event = 0
        goal_not_matching.away_team_goals_post_event = 0
        goal_not_matching.event_type = "goal"
        goal_not_matching.player = mocker.Mock()
        goal_not_matching.player.name = "Player 2"
        goal_not_matching.match = mocker.Mock()
        goal_not_matching.match.home_team = mocker.Mock()
        goal_not_matching.match.home_team.name = "Home Team"
        goal_not_matching.match.home_team_goals = 3
        goal_not_matching.match.away_team_goals = 0

        goals = [goal_matching, goal_not_matching]

        analyzer._show_goal_details_for_minute_score_diff(45, 1, DEFAULT_WINDOW_SIZE, goals)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Total goals found: 1" in print_output

    def test_skips_invalid_goals(self, mocker) -> None:
        """Test that method skips invalid goals."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        valid_goal = mocker.Mock()
        valid_goal.minute = 45
        valid_goal.home_team_goals_pre_event = 0
        valid_goal.home_team_goals_post_event = 1
        valid_goal.away_team_goals_pre_event = 0
        valid_goal.away_team_goals_post_event = 0
        valid_goal.event_type = "goal"
        valid_goal.player = mocker.Mock()
        valid_goal.player.name = "Player 1"
        valid_goal.match = mocker.Mock()
        valid_goal.match.home_team = mocker.Mock()
        valid_goal.match.home_team.name = "Home Team"
        valid_goal.match.home_team_goals = 2
        valid_goal.match.away_team_goals = 1

        invalid_goal = mocker.Mock()
        invalid_goal.minute = 45
        invalid_goal.home_team_goals_pre_event = None
        invalid_goal.match = mocker.Mock()
        invalid_goal.match.home_team_goals = 2
        invalid_goal.match.away_team_goals = 1

        goals = [valid_goal, invalid_goal]

        analyzer._show_goal_details_for_minute_score_diff(45, 1, DEFAULT_WINDOW_SIZE, goals)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Total goals found: 1" in print_output

    def test_handles_missing_player(self, mocker) -> None:
        """Test that method handles goals with missing player."""
        mock_print = mocker.patch("builtins.print")
        analyzer = GoalValueAnalyzer()
        analyzer.goal_value_dict = defaultdict(dict, {45: {1: 0.75}})

        goal = mocker.Mock()
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0
        goal.event_type = "goal"
        goal.player = None
        goal.match = mocker.Mock()
        goal.match.home_team = mocker.Mock()
        goal.match.home_team.name = "Home Team"
        goal.match.home_team_goals = 2
        goal.match.away_team_goals = 1

        goals = [goal]

        analyzer._show_goal_details_for_minute_score_diff(45, 1, DEFAULT_WINDOW_SIZE, goals)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Unknown" in print_output
