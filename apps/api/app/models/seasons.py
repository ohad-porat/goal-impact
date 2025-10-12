"""Season model definition for FBRef scrapers."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Season(Base):
    """Model representing a season in the database."""
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    start_year = Column(Integer)
    end_year = Column(Integer)
    fbref_url = Column(String, unique=True, nullable=False)
    matches_url = Column(String)

    competition_id = Column(Integer, ForeignKey('competitions.id'))

    competition = relationship("Competition", back_populates="seasons")
    matches = relationship("Match", back_populates="season")
    team_stats = relationship("TeamStats", back_populates="season")
