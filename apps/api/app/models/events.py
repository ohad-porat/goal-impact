"""Event model definition for FBRef scrapers."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class Event(Base):
    """Model representing an event (goal, card, etc.) in the database."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    minute = Column(Integer)
    home_team_goals_pre_event = Column(Integer)
    away_team_goals_pre_event = Column(Integer)
    home_team_goals_post_event = Column(Integer)
    away_team_goals_post_event = Column(Integer)
    xg = Column(Float)
    post_shot_xg = Column(Float)
    xg_difference = Column(Float)
    goal_value = Column(Float)

    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))

    match = relationship("Match", back_populates="events")
    player = relationship("Player", back_populates="events")

    __table_args__ = (
        UniqueConstraint(
            "match_id", "player_id", "minute", "event_type", name="unique_match_player_minute_event"
        ),
    )
