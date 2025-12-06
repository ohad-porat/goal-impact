"""Nation model definition for FBRef scrapers."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Nation(Base):
    """Model representing a nation/country in the database."""

    __tablename__ = "nations"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    governing_body = Column(String)
    country_code = Column(String, unique=True, nullable=False)
    fbref_url = Column(String, unique=True, nullable=False)
    clubs_url = Column(String)

    competitions = relationship("Competition", back_populates="nation")
    teams = relationship("Team", back_populates="nation")

    def __repr__(self):
        return (
            f"<Nation(id={self.id}, name={self.name!r}, country_code={self.country_code!r}, "
            f"fbref_url={self.fbref_url!r})>"
        )
