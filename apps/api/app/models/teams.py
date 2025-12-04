"""Team model definition for FBRef scrapers."""

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class Team(Base):
    """Model representing a team/club in the database."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    fbref_id = Column(String, unique=True, nullable=False)
    fbref_url = Column(String)

    nation_id = Column(Integer, ForeignKey("nations.id"))

    nation = relationship("Nation", back_populates="teams")
    team_stats = relationship("TeamStats", back_populates="team")

    __table_args__ = (UniqueConstraint("fbref_url", name="unique_non_null_fbref_url"),)
