"""Unit tests for player stats goal value updater."""

import pytest

from app.core.goal_value.player_stats_updater import PlayerStatsGoalValueUpdater
from app.tests.utils.helpers import create_mock_session_with_queries


class TestInit:
    """Tests for __init__ method."""

    def test_initializes_with_dependencies(self, mocker):
        """Test that updater initializes with session and counters."""
        mocker.patch("app.core.goal_value.player_stats_updater.Session")
        updater = PlayerStatsGoalValueUpdater()

        assert updater.session is not None
        assert updater.aggregated_data == {}
        assert updater.update_count == 0
        assert updater.error_count == 0
        assert updater.errors == []
        assert updater.all_player_stats is None


class TestAggregatePlayerGoalValues:
    """Tests for _aggregate_player_goal_values method."""

    def test_initializes_all_player_stats_with_zeros(self, mocker):
        """Test that method initializes all player stats with zero values."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()

        player_stat1 = mocker.Mock()
        player_stat1.player_id = 1
        player_stat1.season_id = 1
        player_stat1.team_id = 1

        player_stat2 = mocker.Mock()
        player_stat2.player_id = 2
        player_stat2.season_id = 1
        player_stat2.team_id = 2

        updater.session = create_mock_session_with_queries(mocker, [player_stat1, player_stat2], [])

        updater._aggregate_player_goal_values()

        assert (1, 1, 1) in updater.aggregated_data
        assert (2, 1, 2) in updater.aggregated_data
        assert updater.aggregated_data[(1, 1, 1)]["total_goal_value"] == 0.0
        assert updater.aggregated_data[(1, 1, 1)]["gv_avg"] == 0.0
        assert updater.aggregated_data[(1, 1, 1)]["goal_count"] == 0

    def test_aggregates_goal_values_by_player_season_team(self, mocker):
        """Test that method aggregates goal values by player, season, and team."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()

        player_stat = mocker.Mock()
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        event1 = (1, 1, 1, 0, 0, 0, 0.5, 1, 2)
        event2 = (1, 1, 1, 0, 0, 0, 0.75, 1, 2)

        updater.session = create_mock_session_with_queries(mocker, [player_stat], [event1, event2])

        updater._aggregate_player_goal_values()

        assert updater.aggregated_data[(1, 1, 1)]["total_goal_value"] == 1.25
        assert updater.aggregated_data[(1, 1, 1)]["goal_count"] == 2
        assert updater.aggregated_data[(1, 1, 1)]["gv_avg"] == 0.625

    def test_calculates_gv_avg_correctly(self, mocker):
        """Test that method calculates gv_avg correctly."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()

        player_stat = mocker.Mock()
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        event1 = (1, 1, 1, 0, 0, 0, 0.5, 1, 2)
        event2 = (1, 1, 1, 0, 0, 0, 0.75, 1, 2)
        event3 = (1, 1, 1, 0, 0, 0, 1.0, 1, 2)

        updater.session = create_mock_session_with_queries(mocker, [player_stat], [event1, event2, event3])

        updater._aggregate_player_goal_values()

        assert updater.aggregated_data[(1, 1, 1)]["gv_avg"] == 0.75

    def test_skips_events_with_unclear_scoring_team(self, mocker):
        """Test that method skips events where scoring team is unclear."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()

        player_stat = mocker.Mock()
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        event = (1, 1, 1, 1, 0, 0, 0.5, 1, 2)

        updater.session = create_mock_session_with_queries(mocker, [player_stat], [event])

        updater._aggregate_player_goal_values()

        assert updater.aggregated_data[(1, 1, 1)]["goal_count"] == 0

    def test_only_includes_goals_for_matching_team(self, mocker):
        """Test that method only includes goals for matching team."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()

        player_stat = mocker.Mock()
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        event1 = (1, 1, 1, 0, 0, 0, 0.5, 1, 2)
        event2 = (1, 1, 0, 0, 1, 0, 0.75, 1, 2)

        updater.session = create_mock_session_with_queries(mocker, [player_stat], [event1, event2])

        updater._aggregate_player_goal_values()

        assert updater.aggregated_data[(1, 1, 1)]["goal_count"] == 1
        assert updater.aggregated_data[(1, 1, 1)]["total_goal_value"] == 0.5

    def test_handles_zero_goals(self, mocker):
        """Test that method handles player stats with zero goals."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()

        player_stat = mocker.Mock()
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        updater.session = create_mock_session_with_queries(mocker, [player_stat], [])

        updater._aggregate_player_goal_values()

        assert updater.aggregated_data[(1, 1, 1)]["goal_count"] == 0
        assert updater.aggregated_data[(1, 1, 1)]["gv_avg"] == 0.0


class TestCommitBatch:
    """Tests for _commit_batch method."""

    def test_commits_batch_successfully(self, mocker):
        """Test that method commits batch successfully."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        update_data = [{"id": 1, "goal_value": 0.5, "gv_avg": 0.5}]

        result = updater._commit_batch(update_data, 0, False)

        updater.session.bulk_update_mappings.assert_called_once()
        updater.session.commit.assert_called_once()
        assert result == 1

    def test_handles_commit_errors(self, mocker):
        """Test that method handles commit errors."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit.side_effect = Exception("Commit error")

        update_data = [{"id": 1, "goal_value": 0.5, "gv_avg": 0.5}]

        result = updater._commit_batch(update_data, 0, False)

        assert result == 0
        assert len(updater.errors) == 1
        assert updater.error_count == 1

    def test_prints_final_prefix_for_final_batch(self, mocker):
        """Test that method prints final prefix for final batch."""
        mock_print = mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        update_data = [{"id": 1, "goal_value": 0.5, "gv_avg": 0.5}]

        updater._commit_batch(update_data, 0, True)

        print_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "final" in print_output.lower()


class TestBatchUpdate:
    """Tests for _batch_update method."""

    def test_updates_all_player_stats(self, mocker):
        """Test that method updates all player stats."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        player_stat1 = mocker.Mock()
        player_stat1.id = 1
        player_stat1.player_id = 1
        player_stat1.season_id = 1
        player_stat1.team_id = 1

        player_stat2 = mocker.Mock()
        player_stat2.id = 2
        player_stat2.player_id = 2
        player_stat2.season_id = 1
        player_stat2.team_id = 2

        updater.all_player_stats = [player_stat1, player_stat2]
        updater.aggregated_data = {
            (1, 1, 1): {"total_goal_value": 1.5, "gv_avg": 0.75, "goal_count": 2},
            (2, 1, 2): {"total_goal_value": 2.0, "gv_avg": 1.0, "goal_count": 2},
        }

        updater._batch_update()

        assert updater.update_count == 2
        assert updater.session.bulk_update_mappings.called

    def test_handles_errors_gracefully(self, mocker):
        """Test that method handles errors gracefully."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        player_stat = mocker.Mock()
        player_stat.id = 1
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        updater.all_player_stats = [player_stat]
        updater.aggregated_data = {}

        updater._batch_update()

        assert updater.error_count == 1
        assert len(updater.errors) == 1

    def test_rounds_values_to_three_decimals(self, mocker):
        """Test that method rounds values to three decimal places."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        player_stat = mocker.Mock()
        player_stat.id = 1
        player_stat.player_id = 1
        player_stat.season_id = 1
        player_stat.team_id = 1

        updater.all_player_stats = [player_stat]
        updater.aggregated_data = {
            (1, 1, 1): {"total_goal_value": 1.234567, "gv_avg": 0.987654, "goal_count": 1},
        }

        updater._batch_update()

        call_args = updater.session.bulk_update_mappings.call_args
        update_data = call_args[0][1]
        assert update_data[0]["goal_value"] == 1.235
        assert update_data[0]["gv_avg"] == 0.988


class TestPrintSummary:
    """Tests for _print_summary method."""

    def test_prints_summary(self, mocker):
        """Test that method prints summary information."""
        mock_print = mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.update_count = 100
        updater.error_count = 5
        updater.aggregated_data = {
            (1, 1, 1): {"total_goal_value": 1.5, "gv_avg": 0.75, "goal_count": 2},
            (2, 1, 2): {"total_goal_value": 0.0, "gv_avg": 0.0, "goal_count": 0},
        }

        updater._print_summary()

        assert mock_print.call_count >= 5
        print_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "100" in print_output
        assert "5" in print_output

    def test_prints_errors_when_few_errors(self, mocker):
        """Test that method prints all errors when there are few errors."""
        mock_print = mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.update_count = 100
        updater.error_count = 2
        updater.errors = ["Error 1", "Error 2"]
        updater.aggregated_data = {}

        updater._print_summary()

        print_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "Error 1" in print_output
        assert "Error 2" in print_output

    def test_prints_first_10_errors_when_many_errors(self, mocker):
        """Test that method prints first 10 errors when there are many errors."""
        mock_print = mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.update_count = 100
        updater.error_count = 15
        updater.errors = [f"Error {i}" for i in range(15)]
        updater.aggregated_data = {}

        updater._print_summary()

        print_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "first 10" in print_output.lower() or "15" in print_output


class TestUpdatePlayerStatsForCombinations:
    """Tests for update_player_stats_for_combinations method."""

    def test_returns_early_when_no_combinations(self, mocker):
        """Test that method returns early when no combinations provided."""
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        updater.update_player_stats_for_combinations([])

        updater.session.query.assert_not_called()

    def test_updates_specific_combinations(self, mocker):
        """Test that method updates specific combinations."""
        mocker.patch("app.core.goal_value.player_stats_updater.logger")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        event1 = (0.5, 1, 0, 0, 0, 1, 2)
        event2 = (0.75, 1, 0, 0, 0, 1, 2)

        mock_query = mocker.Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = [event1, event2]
        updater.session.query.return_value = mock_query

        player_stat = mocker.Mock()
        player_stat.id = 1
        mock_query2 = mocker.Mock()
        mock_query2.filter_by.return_value.first.return_value = player_stat
        updater.session.query.side_effect = [mock_query, mock_query2]

        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        updater.update_player_stats_for_combinations([(1, 1, 1)])

        updater.session.bulk_update_mappings.assert_called_once()
        updater.session.commit.assert_called_once()

    def test_filters_goals_by_team_id(self, mocker):
        """Test that method filters goals by team_id."""
        mocker.patch("app.core.goal_value.player_stats_updater.logger")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        event1 = (0.5, 1, 0, 0, 0, 1, 2)
        event2 = (0.75, 0, 0, 1, 0, 1, 2)

        mock_query = mocker.Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = [event1, event2]
        updater.session.query.return_value = mock_query

        player_stat = mocker.Mock()
        player_stat.id = 1
        mock_query2 = mocker.Mock()
        mock_query2.filter_by.return_value.first.return_value = player_stat
        updater.session.query.side_effect = [mock_query, mock_query2]

        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        updater.update_player_stats_for_combinations([(1, 1, 1)])

        call_args = updater.session.bulk_update_mappings.call_args
        update_data = call_args[0][1]
        assert len(update_data) == 1
        assert update_data[0]["goal_value"] == 0.5
        assert all(item["goal_value"] != 0.75 for item in update_data)

    def test_handles_zero_goals(self, mocker):
        """Test that method handles combinations with zero goals."""
        mocker.patch("app.core.goal_value.player_stats_updater.logger")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        mock_query = mocker.Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = []
        updater.session.query.return_value = mock_query

        player_stat = mocker.Mock()
        player_stat.id = 1
        mock_query2 = mocker.Mock()
        mock_query2.filter_by.return_value.first.return_value = player_stat
        updater.session.query.side_effect = [mock_query, mock_query2]

        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit = mocker.Mock()

        updater.update_player_stats_for_combinations([(1, 1, 1)])

        call_args = updater.session.bulk_update_mappings.call_args
        update_data = call_args[0][1]
        assert update_data[0]["goal_value"] == 0.0
        assert update_data[0]["gv_avg"] == 0.0

    def test_handles_missing_player_stat(self, mocker):
        """Test that method handles missing player stat."""
        mocker.patch("app.core.goal_value.player_stats_updater.logger")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        mock_query = mocker.Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = []
        updater.session.query.return_value = mock_query

        mock_query2 = mocker.Mock()
        mock_query2.filter_by.return_value.first.return_value = None
        updater.session.query.side_effect = [mock_query, mock_query2]

        updater.update_player_stats_for_combinations([(1, 1, 1)])

        updater.session.bulk_update_mappings.assert_not_called()

    def test_handles_exceptions(self, mocker):
        """Test that method handles exceptions gracefully."""
        mocker.patch("app.core.goal_value.player_stats_updater.logger")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.query.side_effect = RuntimeError("Database error")

        updater.update_player_stats_for_combinations([(1, 1, 1)])

        assert updater.error_count == 1

    def test_rolls_back_on_batch_error(self, mocker):
        """Test that method rolls back on batch update error."""
        mocker.patch("app.core.goal_value.player_stats_updater.logger")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()

        mock_query = mocker.Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = []
        updater.session.query.return_value = mock_query

        player_stat = mocker.Mock()
        player_stat.id = 1
        mock_query2 = mocker.Mock()
        mock_query2.filter_by.return_value.first.return_value = player_stat
        updater.session.query.side_effect = [mock_query, mock_query2]

        updater.session.bulk_update_mappings = mocker.Mock()
        updater.session.commit.side_effect = RuntimeError("Commit error")
        updater.session.rollback = mocker.Mock()

        with pytest.raises(RuntimeError, match="Commit error"):
            updater.update_player_stats_for_combinations([(1, 1, 1)])

        updater.session.rollback.assert_called_once()


class TestRun:
    """Tests for run method."""

    def test_runs_full_update_flow(self, mocker):
        """Test that run method executes full update flow."""
        mocker.patch("builtins.print")
        updater = PlayerStatsGoalValueUpdater()
        updater.session = mocker.Mock()
        updater.session.query.return_value.all.return_value = []

        mock_query = mocker.Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = []
        updater.session.query.return_value = mock_query

        updater._aggregate_player_goal_values = mocker.Mock()
        updater._batch_update = mocker.Mock()
        updater._print_summary = mocker.Mock()

        updater.run()

        updater._aggregate_player_goal_values.assert_called_once()
        updater._batch_update.assert_called_once()
        updater._print_summary.assert_called_once()
