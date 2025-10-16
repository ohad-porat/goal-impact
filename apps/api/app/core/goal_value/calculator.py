"""Main Goal Value Calculator - orchestrates the calculation process."""

from collections import defaultdict
from .data_processor import GoalDataProcessor
from .repository import GoalValueRepository
from .utils import (
    MIN_SCORE_DIFF,
    MAX_SCORE_DIFF,
    MIN_MINUTE,
    MAX_MINUTE,
    NOISE_THRESHOLD,
    get_score_diff_range,
    get_minute_range
)


class GoalValueCalculator:
    """Main calculator for goal value and points added statistics."""
    
    def __init__(self):
        self.data_processor = GoalDataProcessor()
        self.repository = GoalValueRepository()
        self.goal_value_dict = defaultdict(dict)
    
    def run(self):
        """Main execution method."""
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
        """Calculate goal_value for all minutes 1-95."""
        for minute in get_minute_range():
            for score_diff in get_score_diff_range():
                key = (minute, score_diff)
                if key in aggregated_data and aggregated_data[key]['total'] > 0:
                    window_start, window_end = self._get_calculation_window(minute)
                    minute_data = self.data_processor.get_window_data(
                        aggregated_data, window_start, window_end
                    )
                    
                    if minute_data[score_diff]['total'] > 0:
                        goal_value = self._calculate_goal_value_for_score_diff(minute_data[score_diff])
                        if minute not in self.goal_value_dict:
                            self.goal_value_dict[minute] = {}
                        self.goal_value_dict[minute][score_diff] = round(goal_value, 3)
        
        self._enforce_minimal_monotonicity()
    
    def _get_calculation_window(self, minute):
        """Get calculation window for a specific minute."""
        window_start = max(MIN_MINUTE, minute - 2)
        window_end = min(MAX_MINUTE, minute + 2)
        return window_start, window_end
    
    def _calculate_goal_value_for_score_diff(self, score_diff_data):
        """Calculate goal value for a specific score difference."""
        return (score_diff_data['win'] + score_diff_data['draw'] / 3) / score_diff_data['total']
    
    def _enforce_minimal_monotonicity(self):
        """Fix small negative margins by rounding up to 0 for noise tolerance."""
        for minute in get_minute_range():
            if minute in self.goal_value_dict:
                for score_diff in range(MIN_SCORE_DIFF, MAX_SCORE_DIFF):
                    current_value = self.goal_value_dict[minute].get(score_diff)
                    next_value = self.goal_value_dict[minute].get(score_diff + 1)
                    
                    if current_value is not None and next_value is not None:
                        margin = next_value - current_value
                        if 0 > margin > NOISE_THRESHOLD:
                            self.goal_value_dict[minute][score_diff + 1] = current_value
    
