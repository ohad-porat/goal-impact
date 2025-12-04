"""Unit tests for Season model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Season
from app.tests.utils.factories import CompetitionFactory, SeasonFactory


class TestSeasonModel:
    """Test Season model functionality."""

    def test_create_season(self, db_session):
        """Test creating a season with all fields."""
        competition = CompetitionFactory()
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            fbref_url="/en/seasons/2023-2024/",
            competition=competition,
        )
        db_session.commit()

        assert season.id is not None
        assert season.start_year == 2023
        assert season.end_year == 2024
        assert season.competition_id == competition.id

    def test_season_unique_fbref_url(self, db_session):
        """Test that fbref_url must be unique."""
        SeasonFactory(fbref_url="/en/seasons/2023-2024/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            SeasonFactory(fbref_url="/en/seasons/2023-2024/")
            db_session.commit()

    def test_season_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            season = Season(start_year=2023, end_year=2024)
            db_session.add(season)
            db_session.commit()

    def test_season_foreign_key_to_competition(self, db_session):
        """Test foreign key relationship to Competition."""
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition)
        db_session.commit()

        assert season.competition == competition

    def test_season_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        season = SeasonFactory(competition=None, start_year=None, end_year=None, matches_url=None)
        db_session.commit()

        assert season.competition_id is None
        assert season.competition is None
        assert season.start_year is None
        assert season.end_year is None
        assert season.matches_url is None
