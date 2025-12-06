"""Match model definition for FBRef scrapers."""

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Match(Base):
    """Model representing a match in the database."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    home_team_goals = Column(Integer)
    away_team_goals = Column(Integer)
    date = Column(Date)
    fbref_id = Column(String, unique=True, nullable=False)
    fbref_url = Column(String, unique=True, nullable=False)

    season_id = Column(Integer, ForeignKey("seasons.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))

    season = relationship("Season", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    events = relationship("Event", back_populates="match")

    def __repr__(self):
        return (
            f"<Match(id={self.id}, date={self.date}, "
            f"home_goals={self.home_team_goals}, away_goals={self.away_team_goals}, "
            f"fbref_id={self.fbref_id!r})>"
        )
