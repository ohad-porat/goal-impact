"""Player model definition for FBRef scrapers."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Player(Base):
    """Model representing a player in the database."""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fbref_id = Column(String, unique=True, nullable=False)
    fbref_url = Column(String, unique=True, nullable=False)

    nation_id = Column(Integer, ForeignKey('nations.id'))

    nation = relationship("Nation")
    events = relationship("Event", back_populates="player")
    player_stats = relationship("PlayerStats", back_populates="player")
