"""Season model definition for FBRef scrapers."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from .base import Base


class Season(Base):
    """Model representing a season in the database."""

    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    start_year = Column(Integer)
    end_year = Column(Integer)
    fbref_url = Column(String, unique=True, nullable=False)
    matches_url = Column(String)

    competition_id = Column(Integer, ForeignKey("competitions.id"))

    competition = relationship("Competition", back_populates="seasons")
    matches = relationship("Match", back_populates="season")
    team_stats = relationship("TeamStats", back_populates="season")
    player_stats = relationship("PlayerStats", back_populates="season")

    __table_args__ = (
        CheckConstraint(
            "(start_year IS NULL OR end_year IS NULL) OR (start_year <= end_year)",
            name="check_season_years",
        ),
    )

    @validates("start_year", "end_year")
    def validate_season_years(self, key, value):
        """Validate that start_year is less than or equal to end_year when both are provided."""
        if value is not None:
            if key == "end_year" and self.start_year is not None and value < self.start_year:
                raise ValueError(
                    f"end_year ({value}) must be greater than or equal to start_year ({self.start_year})"
                )
            elif key == "start_year" and self.end_year is not None and value > self.end_year:
                raise ValueError(
                    f"start_year ({value}) must be less than or equal to end_year ({self.end_year})"
                )
        return value

    def __repr__(self):
        return (
            f"<Season(id={self.id}, start_year={self.start_year}, end_year={self.end_year}, "
            f"competition_id={self.competition_id}, fbref_url={self.fbref_url!r})>"
        )
