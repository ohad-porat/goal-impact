"""StatsCalculationMetadata model definition."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .base import Base


class StatsCalculationMetadata(Base):
    """Model representing metadata for statistics calculations."""

    __tablename__ = "stats_calculation_metadata"

    id = Column(Integer, primary_key=True)
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_goals_processed = Column(Integer, nullable=False)
    version = Column(String, nullable=False, default="1.0")

    def __repr__(self):
        return f"<StatsCalculationMetadata(id={self.id}, date={self.calculation_date}, goals={self.total_goals_processed})>"
