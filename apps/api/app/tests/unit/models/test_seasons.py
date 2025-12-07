"""Unit tests for Season model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Season
from app.tests.utils.factories import CompetitionFactory, SeasonFactory


class TestSeasonModel:
    """Test Season model functionality."""

    def test_create_season(self, db_session) -> None:
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

    def test_season_unique_fbref_url(self, db_session) -> None:
        """Test that fbref_url must be unique."""
        SeasonFactory(fbref_url="/en/seasons/2023-2024/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            SeasonFactory(fbref_url="/en/seasons/2023-2024/")
            db_session.commit()

    def test_season_required_fields(self, db_session) -> None:
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            season = Season(start_year=2023, end_year=2024)
            db_session.add(season)
            db_session.commit()

    def test_season_foreign_key_to_competition(self, db_session) -> None:
        """Test foreign key relationship to Competition."""
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition)
        db_session.commit()

        assert season.competition == competition

    def test_season_optional_fields(self, db_session) -> None:
        """Test that optional fields can be null."""
        season = SeasonFactory(competition=None, start_year=None, end_year=None, matches_url=None)
        db_session.commit()

        assert season.competition_id is None
        assert season.competition is None
        assert season.start_year is None
        assert season.end_year is None
        assert season.matches_url is None

    def test_season_year_validation_valid(self, db_session) -> None:
        """Test that start_year < end_year is valid."""
        competition = CompetitionFactory()
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/seasons/2023-2024/",
        )
        db_session.commit()

        assert season.start_year == 2023
        assert season.end_year == 2024

    def test_season_year_validation_invalid(self, db_session) -> None:
        """Test that end_year < start_year raises ValueError."""
        from app.models import Season

        competition = CompetitionFactory()

        with pytest.raises(ValueError, match="end_year.*must be greater than or equal"):
            Season(
                start_year=2024,
                end_year=2023,
                fbref_url="/en/seasons/2024-2023/",
                competition_id=competition.id,
            )

    def test_season_year_validation_equal_years(self, db_session) -> None:
        """Test that start_year == end_year is allowed for single-year seasons."""
        from app.models import Season

        competition = CompetitionFactory()
        season = Season(
            start_year=2023,
            end_year=2023,
            fbref_url="/en/seasons/2023-2023/",
            competition_id=competition.id,
        )
        db_session.add(season)
        db_session.commit()

        assert season.start_year == 2023
        assert season.end_year == 2023

    def test_season_year_validation_one_null_allowed(self, db_session) -> None:
        """Test that one of start_year or end_year can be null."""
        competition = CompetitionFactory()
        season1 = SeasonFactory(
            start_year=2023, end_year=None, competition=competition, fbref_url="/en/seasons/2023/"
        )
        season2 = SeasonFactory(
            start_year=None, end_year=2024, competition=competition, fbref_url="/en/seasons/2024/"
        )
        db_session.commit()

        assert season1.start_year == 2023
        assert season1.end_year is None
        assert season2.start_year is None
        assert season2.end_year == 2024
