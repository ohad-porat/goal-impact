"""TeamStats model definition for FBRef scrapers."""

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class TeamStats(Base):
    """Model representing team statistics in the database."""
    __tablename__ = 'team_stats'

    id = Column(Integer, primary_key=True)
    fbref_url = Column(String, unique=True, nullable=False)
    goal_logs_url = Column(String)
    ranking = Column(Integer)
    matches_played = Column(Integer)
    wins = Column(Integer)
    draws = Column(Integer)
    losses = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    goal_difference = Column(Integer)
    points = Column(Integer)
    points_per_match = Column(Float)
    xg = Column(Float)
    xga = Column(Float)
    xgd = Column(Float)
    xgd_per_90 = Column(Float)

    team_id = Column(Integer, ForeignKey('teams.id'))
    season_id = Column(Integer, ForeignKey('seasons.id'))

    team = relationship("Team", back_populates="team_stats")
    season = relationship("Season", back_populates="team_stats")
