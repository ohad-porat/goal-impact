"""Event model definition for FBRef scrapers."""

from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship, validates

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
        CheckConstraint("minute >= 0 AND minute <= 120", name="check_minute_range"),
    )

    @validates("minute")
    def validate_minute(self, _key, minute):
        """Validate that minute is within reasonable range (0-120 including stoppage time)."""
        if minute is not None and (minute < 0 or minute > 120):
            raise ValueError(f"Minute must be between 0 and 120, got {minute}")
        return minute

    @validates("event_type")
    def validate_event_type(self, _key, event_type):
        """Validate event_type is one of the allowed types: goal, own goal, or assist."""
        if event_type is not None:
            valid_types = {"goal", "own goal", "assist"}
            if event_type not in valid_types:
                raise ValueError(
                    f"Invalid event_type: {event_type!r}. Must be one of {sorted(valid_types)}"
                )
        return event_type

    def __repr__(self):
        return (
            f"<Event(id={self.id}, type={self.event_type!r}, minute={self.minute}, "
            f"match_id={self.match_id}, player_id={self.player_id})>"
        )
