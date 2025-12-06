"""Competition model definition for FBRef scrapers."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Competition(Base):
    """Model representing a competition/league in the database."""

    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    competition_type = Column(String)
    tier = Column(String)
    fbref_id = Column(String, unique=True, nullable=False)
    fbref_url = Column(String, unique=True, nullable=False)

    nation_id = Column(Integer, ForeignKey("nations.id"))

    nation = relationship("Nation", back_populates="competitions")
    seasons = relationship("Season", back_populates="competition")

    def __repr__(self):
        return (
            f"<Competition(id={self.id}, name={self.name!r}, "
            f"type={self.competition_type!r}, tier={self.tier!r}, fbref_id={self.fbref_id!r})>"
        )
