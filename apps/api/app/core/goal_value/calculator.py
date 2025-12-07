"""Main Goal Value Calculator - orchestrates the calculation process."""

from collections import defaultdict

from .data_processor import GoalDataProcessor
from .repository import GoalValueRepository
from .utils import (
    MAX_MINUTE,
    MAX_SCORE_DIFF,
    MIN_MINUTE,
    MIN_SCORE_DIFF,
    NOISE_THRESHOLD,
    get_minute_range,
    get_score_diff_range,
)


class GoalValueCalculator:
    """Main calculator for goal value and points added statistics."""

    def __init__(self):
        self.data_processor = GoalDataProcessor()
        self.repository = GoalValueRepository()
        self.goal_value_dict = defaultdict(dict)

    def run(self):
        """Main execution method.

        Orchestrates the complete goal value calculation process:
        1. Query all goals from database
        2. Aggregate goal data by minute and score difference
        3. Calculate goal values using window-based approach
        4. Persist results to database
        5. Save calculation metadata
        """
        print("Starting goal value calculation...")

        goals = self.data_processor.query_goals()
        print(f"Found {len(goals)} goals to process")

        aggregated_data = self.data_processor.process_goal_data(goals)
        print(f"Aggregated data for {len(aggregated_data)} (minute, score_diff) combinations")

        self._calculate_goal_value(aggregated_data)
        print(f"Calculated goal_value for {len(self.goal_value_dict)} minutes")

        self.repository.persist_goal_values(self.goal_value_dict)
        print("Persisted goal_value data to database")

        self.repository.save_metadata(len(goals))
        print("Saved calculation metadata")

        print("Goal value calculation completed successfully!")

    def _calculate_goal_value(self, aggregated_data):
        """Calculate goal_value for all minutes 1-95.

        Uses a sliding window approach: for each minute/score_diff combination,
        calculates goal value based on outcomes in a 5-minute window around that minute.

        Args:
            aggregated_data: Dictionary keyed by (minute, score_diff) with outcome counts
        """
        for minute in get_minute_range():
            for score_diff in get_score_diff_range():
                key = (minute, score_diff)
                if key in aggregated_data and aggregated_data[key]["total"] > 0:
                    window_start, window_end = self._get_calculation_window(minute)
                    minute_data = self.data_processor.get_window_data(
                        aggregated_data, window_start, window_end
                    )

                    if minute_data[score_diff]["total"] > 0:
                        goal_value = self._calculate_goal_value_for_score_diff(
                            minute_data[score_diff]
                        )
                        if minute not in self.goal_value_dict:
                            self.goal_value_dict[minute] = {}
                        self.goal_value_dict[minute][score_diff] = round(goal_value, 3)

        self._enforce_minimal_monotonicity()

    def _get_calculation_window(self, minute):
        """Get calculation window for a specific minute.

        Uses a 5-minute window (±2 minutes) around the target minute, clamped to valid range.

        Args:
            minute: Target minute

        Returns:
            Tuple of (window_start, window_end)
        """
        window_start = max(MIN_MINUTE, minute - 2)
        window_end = min(MAX_MINUTE, minute + 2)
        return window_start, window_end

    def _calculate_goal_value_for_score_diff(self, score_diff_data):
        """Calculate goal value for a specific score difference.

        Formula: (wins + draws/3) / total_goals
        Draws are weighted as 1/3 of a win since they're worth 1/3 of the points.

        Args:
            score_diff_data: Dictionary with "win", "draw", and "total" counts

        Returns:
            Goal value as float
        """
        return (score_diff_data["win"] + score_diff_data["draw"] / 3) / score_diff_data["total"]

    def _enforce_minimal_monotonicity(self):
        """Fix small negative margins by rounding up to 0 for noise tolerance.

        Ensures goal values are monotonically increasing with score difference.
        If a small negative margin exists (within NOISE_THRESHOLD), adjusts the
        higher score_diff value to match the lower one.
        """
        for minute in get_minute_range():
            if minute in self.goal_value_dict:
                for score_diff in range(MIN_SCORE_DIFF, MAX_SCORE_DIFF):
                    current_value = self.goal_value_dict[minute].get(score_diff)
                    next_value = self.goal_value_dict[minute].get(score_diff + 1)

                    if current_value is not None and next_value is not None:
                        margin = next_value - current_value
                        if 0 > margin > NOISE_THRESHOLD:
                            self.goal_value_dict[minute][score_diff + 1] = current_value
