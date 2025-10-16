"""Goal data processing functionality."""

from collections import defaultdict
from sqlalchemy import or_
from app.core.database import Session
from app.models import Event
from .utils import (
    MIN_SCORE_DIFF,
    MAX_SCORE_DIFF,
    MIN_MINUTE,
    MAX_MINUTE,
    calculate_outcome,
    validate_goal_data,
    get_score_diff_range,
    get_minute_range
)


class GoalDataProcessor:
    """Handles goal data querying and processing."""
    
    def __init__(self):
        self.session = Session()
    
    def query_goals(self):
        """Query all goals from the database."""
        return self.session.query(Event).filter(
            or_(Event.event_type == "goal", Event.event_type == "own goal")
        ).all()
    
    def process_goal_data(self, goals):
        """Process goals and aggregate by (minute, score_diff)."""
        aggregated_data = defaultdict(lambda: {'win': 0, 'draw': 0, 'loss': 0, 'total': 0})
        
        for goal in goals:
            if not validate_goal_data(goal):
                continue
            
            home_scored = goal.home_team_goals_post_event > goal.home_team_goals_pre_event
            
            if home_scored:
                score_diff = goal.home_team_goals_post_event - goal.away_team_goals_post_event
                scoring_team_final = goal.match.home_team_goals
                opponent_final = goal.match.away_team_goals
            else:
                score_diff = goal.away_team_goals_post_event - goal.home_team_goals_post_event
                scoring_team_final = goal.match.away_team_goals
                opponent_final = goal.match.home_team_goals
            
            outcome = calculate_outcome(scoring_team_final, opponent_final)
            
            minute = goal.minute
            if MIN_SCORE_DIFF <= score_diff <= MAX_SCORE_DIFF:
                aggregated_data[(minute, score_diff)][outcome] += 1
                aggregated_data[(minute, score_diff)]['total'] += 1
        
        return aggregated_data
    
    def get_sample_size_for_minute(self, aggregated_data, minute):
        """Get total sample size for a specific minute across all score_diffs."""
        total_sample = 0
        for score_diff in get_score_diff_range():
            key = (minute, score_diff)
            if key in aggregated_data:
                total_sample += aggregated_data[key]['total']
        return total_sample
    
    def get_window_data(self, aggregated_data, start_minute, end_minute):
        """Get aggregated data for a window of minutes."""
        window_data = {}
        for score_diff in get_score_diff_range():
            window_data[score_diff] = {'win': 0, 'draw': 0, 'loss': 0, 'total': 0}
            
            for minute in range(start_minute, end_minute + 1):
                key = (minute, score_diff)
                if key in aggregated_data:
                    window_data[score_diff]['win'] += aggregated_data[key]['win']
                    window_data[score_diff]['draw'] += aggregated_data[key]['draw']
                    window_data[score_diff]['loss'] += aggregated_data[key]['loss']
                    window_data[score_diff]['total'] += aggregated_data[key]['total']
        
        return window_data
