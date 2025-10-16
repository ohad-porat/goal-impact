"""PlayerStats model definition for FBRef scrapers."""

from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class PlayerStats(Base):
    """Model representing player statistics in the database."""
    __tablename__ = 'player_stats'

    id = Column(Integer, primary_key=True)
    matches_played = Column(Integer)
    matches_started = Column(Integer)
    total_minutes = Column(Integer)
    minutes_divided_90 = Column(Float)
    goals_scored = Column(Integer)
    assists = Column(Integer)
    total_goal_assists = Column(Integer)
    non_pk_goals = Column(Integer)
    pk_made = Column(Integer)
    pk_attempted = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    xg = Column(Float)
    non_pk_xg = Column(Float)
    xag = Column(Float)
    npxg_and_xag = Column(Float)
    progressive_carries = Column(Integer)
    progressive_passes = Column(Integer)
    progressive_passes_received = Column(Integer)
    goal_per_90 = Column(Float)
    assists_per_90 = Column(Float)
    total_goals_assists_per_90 = Column(Float)
    non_pk_goals_per_90 = Column(Float)
    non_pk_goal_and_assists_per_90 = Column(Float)
    xg_per_90 = Column(Float)
    xag_per_90 = Column(Float)
    total_xg_xag_per_90 = Column(Float)
    non_pk_xg_per_90 = Column(Float)
    npxg_and_xag_per_90 = Column(Float)
    goal_value = Column(Float)
    gv_avg = Column(Float)

    player_id = Column(Integer, ForeignKey('players.id'))
    season_id = Column(Integer, ForeignKey('seasons.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))

    player = relationship("Player", back_populates="player_stats")
    season = relationship("Season")
    team = relationship("Team")

    __table_args__ = (
        UniqueConstraint('player_id', 'season_id', 'team_id', name='unique_player_season_team'),
    )
