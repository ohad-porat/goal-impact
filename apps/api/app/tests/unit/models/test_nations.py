"""Unit tests for Nation model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Nation
from app.tests.utils.factories import NationFactory


class TestNationModel:
    """Test Nation model functionality."""

    def test_create_nation(self, db_session) -> None:
        """Test creating a nation with all required fields."""
        nation = NationFactory(
            name="England",
            country_code="ENG",
            fbref_url="/en/countries/ENG/",
            governing_body="The FA",
        )
        db_session.commit()

        assert nation.id is not None
        assert nation.name == "England"
        assert nation.country_code == "ENG"
        assert nation.fbref_url == "/en/countries/ENG/"
        assert nation.governing_body == "The FA"

    def test_nation_unique_name(self, db_session) -> None:
        """Test that nation name must be unique."""
        NationFactory(name="England", country_code="ENG", fbref_url="/en/countries/ENG/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            NationFactory(name="England", country_code="FRA", fbref_url="/en/countries/FRA/")
            db_session.commit()

    def test_nation_unique_country_code(self, db_session) -> None:
        """Test that country_code must be unique."""
        NationFactory(name="England", country_code="ENG", fbref_url="/en/countries/ENG/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            NationFactory(
                name="United Kingdom", country_code="ENG", fbref_url="/en/countries/ENG2/"
            )
            db_session.commit()

    def test_nation_unique_fbref_url(self, db_session) -> None:
        """Test that fbref_url must be unique."""
        NationFactory(name="England", country_code="ENG", fbref_url="/en/countries/ENG/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            NationFactory(name="France", country_code="FRA", fbref_url="/en/countries/ENG/")
            db_session.commit()

    def test_nation_required_fields(self, db_session) -> None:
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            nation = Nation(country_code="ENG", fbref_url="/en/countries/ENG/")
            db_session.add(nation)
            db_session.commit()

    def test_nation_optional_fields(self, db_session) -> None:
        """Test that optional fields can be null."""
        nation = NationFactory(
            name="Test Nation",
            country_code="TST",
            fbref_url="/en/countries/TST/",
            governing_body=None,
            clubs_url=None,
        )
        db_session.commit()

        assert nation.governing_body is None
        assert nation.clubs_url is None
