"""Unit tests for GoalValueLookup model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import GoalValueLookup
from app.tests.utils.factories import GoalValueLookupFactory


class TestGoalValueLookupModel:
    """Test GoalValueLookup model functionality."""

    def test_create_goal_value_lookup(self, db_session):
        """Test creating a goal value lookup entry."""
        lookup = GoalValueLookupFactory(
            minute=45,
            score_diff=1,
            goal_value=0.75
        )
        db_session.commit()
        
        assert lookup.minute == 45
        assert lookup.score_diff == 1
        assert lookup.goal_value == 0.75

    def test_goal_value_lookup_composite_primary_key(self, db_session):
        """Test composite primary key (minute, score_diff)."""
        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.80)
            db_session.commit()

    def test_goal_value_lookup_different_combinations(self, db_session):
        """Test that different minute/score_diff combinations are allowed."""
        lookup1 = GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        db_session.commit()
        
        lookup2 = GoalValueLookupFactory(minute=90, score_diff=1, goal_value=0.80)
        db_session.commit()
        
        lookup3 = GoalValueLookupFactory(minute=45, score_diff=-1, goal_value=0.70)
        db_session.commit()
        
        assert lookup1.minute == 45
        assert lookup2.minute == 90
        assert lookup3.score_diff == -1

    def test_goal_value_lookup_required_fields(self, db_session):
        """Test that all fields are required."""
        with pytest.raises(IntegrityError):
            lookup = GoalValueLookup(
                minute=45,
                score_diff=1,
                goal_value=None
            )
            db_session.add(lookup)
            db_session.commit()

    def test_goal_value_lookup_repr(self, db_session):
        """Test the __repr__ method."""
        lookup = GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        db_session.commit()
        
        repr_str = repr(lookup)
        assert "GoalValueLookup" in repr_str
        assert "45" in repr_str
        assert "1" in repr_str
        assert "0.75" in repr_str
