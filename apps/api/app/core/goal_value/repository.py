"""Goal value data persistence and retrieval."""

from collections import defaultdict
from app.core.database import Session
from app.models import GoalValueLookup, StatsCalculationMetadata


class GoalValueRepository:
    """Handles goal value data persistence and retrieval."""
    
    def __init__(self):
        self.session = Session()
    
    def persist_goal_values(self, goal_value_dict):
        """Persist goal_value data to database."""
        self.session.query(GoalValueLookup).delete()
        
        lookup_records = []
        for minute, score_diff_data in goal_value_dict.items():
            for score_diff, goal_value in score_diff_data.items():
                lookup_records.append(GoalValueLookup(
                    minute=minute,
                    score_diff=score_diff,
                    goal_value=goal_value
                ))
        
        self.session.bulk_save_objects(lookup_records)
        self.session.commit()
    
    def save_metadata(self, total_goals, version='1.0'):
        """Save calculation metadata."""
        metadata = StatsCalculationMetadata(
            total_goals_processed=total_goals,
            version=version
        )
        self.session.add(metadata)
        self.session.commit()
    
    def load_goal_values(self):
        """Load goal_value data from database."""
        goal_value_dict = defaultdict(dict)
        lookup_records = self.session.query(GoalValueLookup).all()
        for record in lookup_records:
            goal_value_dict[record.minute][record.score_diff] = record.goal_value
        return goal_value_dict
