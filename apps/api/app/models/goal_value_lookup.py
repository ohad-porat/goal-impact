"""GoalValueLookup model definition."""

from sqlalchemy import Column, Float, Integer

from .base import Base


class GoalValueLookup(Base):
    """Model representing goal value lookup table."""

    __tablename__ = "goal_value_lookup"

    minute = Column(Integer, primary_key=True)
    score_diff = Column(Integer, primary_key=True)
    goal_value = Column(Float, nullable=False)

    def __repr__(self):
        return f"<GoalValueLookup(minute={self.minute}, score_diff={self.score_diff}, goal_value={self.goal_value})>"
