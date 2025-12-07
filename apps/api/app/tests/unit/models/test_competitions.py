"""Unit tests for Competition model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Competition
from app.tests.utils.factories import CompetitionFactory, NationFactory


class TestCompetitionModel:
    """Test Competition model functionality."""

    def test_create_competition(self, db_session) -> None:
        """Test creating a competition with all fields."""
        nation = NationFactory()
        competition = CompetitionFactory(
            name="Premier League",
            gender="M",
            competition_type="League",
            tier="1",
            fbref_id="9",
            fbref_url="/en/comps/9/",
            nation=nation,
        )
        db_session.commit()

        assert competition.id is not None
        assert competition.name == "Premier League"
        assert competition.gender == "M"
        assert competition.competition_type == "League"
        assert competition.tier == "1"
        assert competition.nation_id == nation.id

    def test_competition_unique_fbref_id(self, db_session) -> None:
        """Test that fbref_id must be unique."""
        CompetitionFactory(fbref_id="9", fbref_url="/en/comps/9/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            CompetitionFactory(fbref_id="9", fbref_url="/en/comps/9-2/")
            db_session.commit()

    def test_competition_unique_fbref_url(self, db_session) -> None:
        """Test that fbref_url must be unique."""
        CompetitionFactory(fbref_id="9", fbref_url="/en/comps/9/")
        db_session.commit()

        with pytest.raises(IntegrityError):
            CompetitionFactory(fbref_id="10", fbref_url="/en/comps/9/")
            db_session.commit()

    def test_competition_required_fields(self, db_session) -> None:
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            competition = Competition(name="Test League", fbref_url="/en/comps/test/")
            db_session.add(competition)
            db_session.commit()

    def test_competition_foreign_key_to_nation(self, db_session) -> None:
        """Test foreign key relationship to Nation."""
        nation = NationFactory()
        competition = CompetitionFactory(nation=nation)
        db_session.commit()

        assert competition.nation == nation

    def test_competition_optional_fields(self, db_session) -> None:
        """Test that optional fields can be null."""
        competition = CompetitionFactory(
            nation=None, name=None, gender=None, competition_type=None, tier=None
        )
        db_session.commit()

        assert competition.nation_id is None
        assert competition.nation is None
        assert competition.name is None
        assert competition.gender is None
        assert competition.competition_type is None
        assert competition.tier is None
