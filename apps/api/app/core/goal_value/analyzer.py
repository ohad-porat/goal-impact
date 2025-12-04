"""Goal value analysis and visualization functionality."""

import pandas as pd

from .data_processor import GoalDataProcessor
from .repository import GoalValueRepository
from .utils import (
    DEFAULT_WINDOW_SIZE,
    calculate_outcome,
    calculate_window_bounds,
    get_minute_range,
    get_score_diff_range,
    validate_goal_data,
)


class GoalValueAnalyzer:
    """Handles goal value analysis and visualization."""

    def __init__(self):
        self.data_processor = GoalDataProcessor()
        self.repository = GoalValueRepository()
        self.goal_value_dict = None

    def _ensure_data_loaded(self):
        """Ensure goal value data is loaded."""
        if self.goal_value_dict is None:
            self.goal_value_dict = self.repository.load_goal_values()

    def export_to_dataframe(self):
        """Export goal_value as pandas DataFrame in wide format for visualization."""
        self._ensure_data_loaded()

        gv_data = {}
        for minute in get_minute_range():
            gv_data[minute] = {
                score_diff: self.goal_value_dict[minute].get(score_diff, None)
                for score_diff in get_score_diff_range()
            }
        goal_value_df = pd.DataFrame.from_dict(gv_data, orient="index")

        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)

        return goal_value_df

    def show_sample_sizes(
        self, specific_minute=None, window_size=DEFAULT_WINDOW_SIZE, score_diff=None
    ):
        """Show sample sizes for minute and score_diff, including window aggregation."""
        self._ensure_data_loaded()

        goals = self.data_processor.query_goals()
        aggregated_data = self.data_processor.process_goal_data(goals)

        if specific_minute:
            if score_diff is not None:
                self._show_sample_sizes_for_minute_score_diff(
                    specific_minute, score_diff, window_size, aggregated_data
                )
            else:
                self._show_sample_sizes_for_minute(specific_minute, window_size, aggregated_data)
        else:
            self._show_sample_sizes_overview(aggregated_data)

    def _show_sample_sizes_for_minute_score_diff(
        self, minute, score_diff, window_size, aggregated_data
    ):
        """Show sample sizes for specific minute and score_diff."""
        print(
            f"Sample sizes for minute {minute}, score_diff {score_diff} (window size: {window_size}):"
        )
        print("Minute | Sample Size | Goal Value | Window Used")
        print("-" * 50)

        window_start, window_end = calculate_window_bounds(minute, window_size)
        window_str = f"Window: {window_start}-{window_end}"

        total_sample = 0
        for min_minute in range(window_start, window_end + 1):
            key = (min_minute, score_diff)
            if key in aggregated_data:
                total_sample += aggregated_data[key]["total"]

        goal_value = self.goal_value_dict[minute].get(score_diff, "N/A")
        print(f"{minute:6d} | {total_sample:11d} | {goal_value:9} | {window_str}")

        if window_end - window_start > 0:
            print("\nBreakdown by individual minutes:")
            print("Minute | Sample Size")
            print("-" * 20)
            for min_minute in range(window_start, window_end + 1):
                key = (min_minute, score_diff)
                if key in aggregated_data:
                    sample = aggregated_data[key]["total"]
                    print(f"{min_minute:6d} | {sample:11d}")
                else:
                    print(f"{min_minute:6d} | {0:11d}")

    def _show_sample_sizes_for_minute(self, minute, window_size, aggregated_data):
        """Show sample sizes for specific minute across all score_diffs."""
        print(f"Sample sizes for minute {minute} (window size: {window_size}):")
        print("Score Diff | Sample Size | Goal Value | Window Minutes")
        print("-" * 60)

        sample_size = self.data_processor.get_sample_size_for_minute(aggregated_data, minute)
        min_sample_size = 20

        if sample_size >= min_sample_size:
            window_minutes = [minute]
            print(f"Using single minute: {minute}")
        else:
            window_start, window_end = calculate_window_bounds(minute, window_size)
            window_minutes = list(range(window_start, window_end + 1))
            print(f"Using window: {window_start}-{window_end}")

        for score_diff in get_score_diff_range():
            total_sample = 0
            for min_minute in window_minutes:
                key = (min_minute, score_diff)
                if key in aggregated_data:
                    total_sample += aggregated_data[key]["total"]

            goal_value = self.goal_value_dict[minute].get(score_diff, "N/A")
            window_str = f"{window_minutes[0]}-{window_minutes[-1]}"
            print(f"{score_diff:9d} | {total_sample:11d} | {goal_value:9} | {window_str}")

    def _show_sample_sizes_overview(self, aggregated_data):
        """Show sample sizes overview for all minutes."""
        print("Sample sizes by minute:")
        print("Minute | Total Goals | Score Diffs with Data")
        print("-" * 50)

        for minute in get_minute_range():
            total_goals = 0
            score_diffs_with_data = 0

            for score_diff in get_score_diff_range():
                key = (minute, score_diff)
                if key in aggregated_data:
                    total_goals += aggregated_data[key]["total"]
                    score_diffs_with_data += 1

            if total_goals > 0:
                print(f"{minute:6d} | {total_goals:11d} | {score_diffs_with_data:20d}")

    def show_goal_details(
        self, specific_minute=None, score_diff=None, window_size=DEFAULT_WINDOW_SIZE
    ):
        """Show detailed information about goals for specific minute/score_diff/window."""
        self._ensure_data_loaded()

        goals = self.data_processor.query_goals()

        if specific_minute and score_diff is not None:
            self._show_goal_details_for_minute_score_diff(
                specific_minute, score_diff, window_size, goals
            )
        else:
            print("Please specify both --minute and --score-diff to see goal details")

    def _show_goal_details_for_minute_score_diff(self, minute, score_diff, window_size, goals):
        """Show goal details for specific minute and score_diff."""
        window_start, window_end = calculate_window_bounds(minute, window_size)
        window_minutes = list(range(window_start, window_end + 1))

        print(
            f"Goal details for minute {minute}, score_diff {score_diff} (window: {window_start}-{window_end}):"
        )
        print(
            "Minute | Team | Player | Event Type | Score Before | Score After | Final Score | Outcome"
        )
        print("-" * 90)

        matching_goals = []
        for goal in goals:
            if goal.minute in window_minutes:
                if not validate_goal_data(goal):
                    continue

                home_scored = goal.home_team_goals_post_event > goal.home_team_goals_pre_event

                if home_scored:
                    goal_score_diff = (
                        goal.home_team_goals_post_event - goal.away_team_goals_post_event
                    )
                    scoring_team = goal.match.home_team.name
                    scoring_team_final = goal.match.home_team_goals
                    opponent_final = goal.match.away_team_goals
                else:
                    goal_score_diff = (
                        goal.away_team_goals_post_event - goal.home_team_goals_post_event
                    )
                    scoring_team = goal.match.away_team.name
                    scoring_team_final = goal.match.away_team_goals
                    opponent_final = goal.match.home_team_goals

                if goal_score_diff == score_diff:
                    outcome = calculate_outcome(scoring_team_final, opponent_final)

                    player_name = goal.player.name if goal.player else "Unknown"
                    event_type = goal.event_type
                    score_before = (
                        f"{goal.home_team_goals_pre_event}-{goal.away_team_goals_pre_event}"
                    )
                    score_after = (
                        f"{goal.home_team_goals_post_event}-{goal.away_team_goals_post_event}"
                    )
                    final_score = f"{goal.match.home_team_goals}-{goal.match.away_team_goals}"

                    print(
                        f"{goal.minute:6d} | {scoring_team:20} | {player_name:20} | {event_type:10} | {score_before:11} | {score_after:10} | {final_score:11} | {outcome}"
                    )
                    matching_goals.append(goal)

        print(f"\nTotal goals found: {len(matching_goals)}")
