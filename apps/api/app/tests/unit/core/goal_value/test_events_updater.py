"""Unit tests for event goal value updater."""

from collections import defaultdict

import pytest

from app.core.goal_value.events_updater import EventGoalValueUpdater

PROGRESS_INTERVAL = 5000
TEST_BATCH_SIZE = 2500


class TestInit:
    """Tests for __init__ method."""

    def test_initializes_with_dependencies(self, mocker) -> None:
        """Test that updater initializes with session and repository."""
        mocker.patch("app.core.goal_value.events_updater.Session")
        updater = EventGoalValueUpdater()

        assert updater.session is not None
        assert updater.repository is not None
        assert updater.goal_value_lookup == {}
        assert updater.missing_data_count == 0
        assert updater.calculation_errors == []


class TestQueryGoalEvents:
    """Tests for _query_goal_events method."""

    def test_queries_goals_and_own_goals(self, db_session) -> None:
        """Test that method queries both goals and own goals."""
        updater = EventGoalValueUpdater()
        updater.session = db_session

        from app.tests.utils.factories import EventFactory, MatchFactory, PlayerFactory

        match = MatchFactory()
        player = PlayerFactory()
        EventFactory(event_type="goal", match=match, player=player)
        EventFactory(event_type="own goal", match=match, player=player)
        EventFactory(event_type="assist", match=match, player=player)
        db_session.commit()

        goals = updater._query_goal_events()

        assert len(goals) == 2
        goal_types = {g.event_type for g in goals}
        assert goal_types == {"goal", "own goal"}

    def test_returns_empty_list_when_no_goals(self, db_session) -> None:
        """Test that method returns empty list when no goals exist."""
        updater = EventGoalValueUpdater()
        updater.session = db_session

        goals = updater._query_goal_events()

        assert goals == []


class TestLookupWinProbability:
    """Tests for _lookup_win_probability method."""

    def test_returns_direct_lookup(self) -> None:
        """Test that method returns value from direct lookup."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {45: {1: 0.75}}

        result = updater._lookup_win_probability(45, 1, 1)

        assert result == 0.75

    def test_returns_fallback_to_minute_minus_one(self) -> None:
        """Test that method falls back to minute-1 when direct lookup fails."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {44: {1: 0.7}}

        result = updater._lookup_win_probability(45, 1, 1)

        assert result == 0.7

    def test_returns_fallback_to_minute_plus_one(self) -> None:
        """Test that method falls back to minute+1 when direct lookup fails."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {46: {1: 0.8}}

        result = updater._lookup_win_probability(45, 1, 1)

        assert result == 0.8

    def test_returns_zero_for_negative_score_diff(self) -> None:
        """Test that method returns 0.0 for negative score_diff when no lookup."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {}

        result = updater._lookup_win_probability(45, -1, 1)

        assert result == 0.0

    def test_returns_one_for_positive_score_diff(self) -> None:
        """Test that method returns 1.0 for positive score_diff when no lookup."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {}

        result = updater._lookup_win_probability(45, 2, 1)

        assert result == 1.0

    def test_returns_half_for_zero_score_diff(self) -> None:
        """Test that method returns 0.5 for zero score_diff when no lookup."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {}

        result = updater._lookup_win_probability(45, 0, 1)

        assert result == 0.5

    def test_clamps_minute_to_95(self) -> None:
        """Test that method clamps minute to 95 for lookup."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {95: {1: 0.9}}

        result = updater._lookup_win_probability(100, 1, 1)

        assert result == 0.9


class TestCalculateSingleGoalValue:
    """Tests for _calculate_single_goal_value method."""

    def test_returns_none_when_missing_pre_event_data(self, mocker) -> None:
        """Test that method returns None when pre-event data is missing."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {45: {1: 0.75}}

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = None
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        result = updater._calculate_single_goal_value(goal)

        assert result is None
        assert updater.missing_data_count == 1

    def test_returns_none_when_missing_post_event_data(self, mocker) -> None:
        """Test that method returns None when post-event data is missing."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {45: {1: 0.75}}

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = None
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        result = updater._calculate_single_goal_value(goal)

        assert result is None
        assert updater.missing_data_count == 1

    def test_returns_none_when_no_team_scored(self, mocker) -> None:
        """Test that method returns None when no team scored."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {45: {1: 0.75}}

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 0
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        result = updater._calculate_single_goal_value(goal)

        assert result is None
        assert len(updater.calculation_errors) == 1

    def test_calculates_goal_value_for_home_goal(self, mocker) -> None:
        """Test that method calculates goal value for home team goal."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {
            45: {0: 0.5, 1: 0.75},
        }

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        result = updater._calculate_single_goal_value(goal)

        assert result == 0.25

    def test_calculates_goal_value_for_away_goal(self, mocker) -> None:
        """Test that method calculates goal value for away team goal."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {
            45: {0: 0.5, 1: 0.75},
        }

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 0
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 1

        result = updater._calculate_single_goal_value(goal)

        assert result == 0.25

    def test_returns_none_when_lookup_fails(self, mocker) -> None:
        """Test that method returns None when lookup fails."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {}

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        updater._lookup_win_probability = mocker.Mock(return_value=None)

        result = updater._calculate_single_goal_value(goal)

        assert result is None
        assert len(updater.calculation_errors) == 1

    def test_rounds_goal_value_to_three_decimals(self, mocker) -> None:
        """Test that method rounds goal value to three decimal places."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {
            45: {0: 0.333333, 1: 0.666666},
        }

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        result = updater._calculate_single_goal_value(goal)

        assert isinstance(result, float)
        assert result == round(result, 3)


class TestCalculateGoalValues:
    """Tests for _calculate_goal_values method."""

    def test_calculates_goal_values_for_all_goals(self, mocker) -> None:
        """Test that method calculates goal values for all goals."""
        mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {
            45: {0: 0.5, 1: 0.75},
        }

        goal1 = mocker.Mock()
        goal1.id = 1
        goal1.minute = 45
        goal1.home_team_goals_pre_event = 0
        goal1.home_team_goals_post_event = 1
        goal1.away_team_goals_pre_event = 0
        goal1.away_team_goals_post_event = 0

        goal2 = mocker.Mock()
        goal2.id = 2
        goal2.minute = 45
        goal2.home_team_goals_pre_event = 1
        goal2.home_team_goals_post_event = 2
        goal2.away_team_goals_pre_event = 0
        goal2.away_team_goals_post_event = 0

        goals = [goal1, goal2]

        update_data = updater._calculate_goal_values(goals)

        assert len(update_data) == 2
        assert update_data[0]["id"] == 1
        assert update_data[0]["goal_value"] == 0.25
        assert update_data[1]["id"] == 2
        assert update_data[1]["goal_value"] == 0.25

    def test_skips_goals_with_none_value(self, mocker) -> None:
        """Test that method skips goals that return None."""
        mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {}

        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = None
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0

        goals = [goal]

        update_data = updater._calculate_goal_values(goals)

        assert len(update_data) == 0

    def test_prints_progress_every_5000_goals(self, mocker) -> None:
        """Test that method prints progress every 5000 goals."""
        mock_print = mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = {
            45: {0: 0.5, 1: 0.75},
        }

        goals = []
        for i in range(PROGRESS_INTERVAL + 1):
            goal = mocker.Mock()
            goal.id = i
            goal.minute = 45
            goal.home_team_goals_pre_event = 0
            goal.home_team_goals_post_event = 1
            goal.away_team_goals_pre_event = 0
            goal.away_team_goals_post_event = 0
            goals.append(goal)

        updater._calculate_goal_values(goals)

        progress_calls = [call for call in mock_print.call_args_list if "Processed" in str(call)]
        assert len(progress_calls) >= 1


class TestBatchUpdate:
    """Tests for _batch_update method."""

    def test_updates_events_in_batches(self, mocker) -> None:
        """Test that method updates events in batches."""
        mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        update_data = [{"id": i, "goal_value": 0.5} for i in range(1, TEST_BATCH_SIZE + 1)]

        updater._batch_update(update_data)

        assert updater.session.bulk_update_mappings.call_count >= 2
        assert updater.session.commit.called

    def test_commits_final_batch(self, mocker) -> None:
        """Test that method commits final batch."""
        mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        update_data = [{"id": 1, "goal_value": 0.5}]

        updater._batch_update(update_data)

        updater.session.bulk_update_mappings.assert_called_once()
        assert updater.session.commit.call_count >= 1


class TestPrintSummary:
    """Tests for _print_summary method."""

    def test_prints_summary(self, mocker) -> None:
        """Test that method prints summary information."""
        mock_print = mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.missing_data_count = 5
        updater.calculation_errors = ["Error 1", "Error 2"]

        updater._print_summary(100, 90)

        assert mock_print.call_count >= 5
        print_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "100" in print_output
        assert "90" in print_output
        assert "5" in print_output

    def test_prints_errors_when_few_errors(self, mocker) -> None:
        """Test that method prints all errors when there are few errors."""
        mock_print = mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.calculation_errors = ["Error 1", "Error 2"]

        updater._print_summary(100, 90)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "Error 1" in print_output
        assert "Error 2" in print_output

    def test_prints_first_10_errors_when_many_errors(self, mocker) -> None:
        """Test that method prints first 10 errors when there are many errors."""
        mock_print = mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.calculation_errors = [f"Error {i}" for i in range(15)]

        updater._print_summary(100, 90)

        print_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        assert "first 10" in print_output.lower() or "15" in print_output


class TestUpdateGoalValuesForEvents:
    """Tests for update_goal_values_for_events method."""

    def test_returns_early_when_no_event_ids(self, mocker) -> None:
        """Test that method returns early when no event IDs provided."""
        updater = EventGoalValueUpdater()
        updater.repository = mocker.Mock()
        updater.session = mocker.Mock()

        updater.update_goal_values_for_events([])

        updater.repository.load_goal_values.assert_not_called()
        updater.session.query.assert_not_called()

    def test_loads_lookup_if_not_loaded(self, mocker) -> None:
        """Test that method loads lookup if not already loaded."""
        updater = EventGoalValueUpdater()
        updater.repository = mocker.Mock()
        updater.repository.load_goal_values.return_value = defaultdict(dict)
        updater.session = mocker.Mock()
        updater.session.query.return_value.filter.return_value.all.return_value = []
        updater._calculate_goal_values = mocker.Mock(return_value=[])
        updater._batch_update = mocker.Mock()

        updater.update_goal_values_for_events([1, 2])

        updater.repository.load_goal_values.assert_called_once()

    def test_queries_specific_events(self, mocker) -> None:
        """Test that method queries only specific event IDs."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = defaultdict(dict)
        updater.repository = mocker.Mock()
        updater.session = mocker.Mock()
        mock_query = mocker.Mock()
        mock_filter = mocker.Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = []
        updater.session.query.return_value = mock_query
        updater._calculate_goal_values = mocker.Mock(return_value=[])
        updater._batch_update = mocker.Mock()

        updater.update_goal_values_for_events([1, 2, 3])

        assert mock_query.filter.called

    def test_handles_exceptions(self, mocker) -> None:
        """Test that method handles exceptions correctly."""
        updater = EventGoalValueUpdater()
        updater.goal_value_lookup = defaultdict(dict)
        updater.repository = mocker.Mock()
        updater.session = mocker.Mock()
        updater.session.query.side_effect = RuntimeError("Database error")

        with pytest.raises(RuntimeError, match="Database error"):
            updater.update_goal_values_for_events([1])

        assert len(updater.calculation_errors) == 1
        assert "Database error" in updater.calculation_errors[0]


class TestRun:
    """Tests for run method."""

    def test_runs_full_update_flow(self, mocker) -> None:
        """Test that run method executes full update flow."""
        mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.repository = mocker.Mock()
        updater.repository.load_goal_values.return_value = defaultdict(dict)
        updater.session = mocker.Mock()
        goal = mocker.Mock()
        goal.id = 1
        goal.minute = 45
        goal.home_team_goals_pre_event = 0
        goal.home_team_goals_post_event = 1
        goal.away_team_goals_pre_event = 0
        goal.away_team_goals_post_event = 0
        updater._query_goal_events = mocker.Mock(return_value=[goal])
        updater.goal_value_lookup = {45: {0: 0.5, 1: 0.75}}
        updater._batch_update = mocker.Mock()
        updater._print_summary = mocker.Mock()

        updater.run()

        updater.repository.load_goal_values.assert_called_once()
        updater._query_goal_events.assert_called_once()
        updater._batch_update.assert_called_once()
        updater._print_summary.assert_called_once()

    def test_handles_empty_goals_list(self, mocker) -> None:
        """Test that run method handles empty goals list."""
        mocker.patch("builtins.print")
        updater = EventGoalValueUpdater()
        updater.repository = mocker.Mock()
        updater.repository.load_goal_values.return_value = defaultdict(dict)
        updater.session = mocker.Mock()
        updater._query_goal_events = mocker.Mock(return_value=[])
        updater._batch_update = mocker.Mock()

        updater.run()

        updater._batch_update.assert_not_called()
