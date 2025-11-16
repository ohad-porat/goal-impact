"""Unit tests for Team model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Team
from app.tests.utils.factories import TeamFactory, NationFactory


class TestTeamModel:
    """Test Team model functionality."""

    def test_create_team(self, db_session):
        """Test creating a team with all fields."""
        nation = NationFactory()
        team = TeamFactory(
            name="Arsenal",
            gender="M",
            fbref_id="18bb7c10",
            fbref_url="/en/squads/18bb7c10/",
            nation=nation
        )
        db_session.commit()
        
        assert team.id is not None
        assert team.name == "Arsenal"
        assert team.gender == "M"
        assert team.fbref_id == "18bb7c10"
        assert team.nation_id == nation.id

    def test_team_unique_fbref_id(self, db_session):
        """Test that fbref_id must be unique."""
        TeamFactory(fbref_id="18bb7c10", fbref_url="/en/squads/18bb7c10/")
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            TeamFactory(fbref_id="18bb7c10", fbref_url="/en/squads/18bb7c10-2/")
            db_session.commit()

    def test_team_unique_fbref_url(self, db_session):
        """Test that fbref_url must be unique when not null."""
        TeamFactory(fbref_id="18bb7c10", fbref_url="/en/squads/18bb7c10/")
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            TeamFactory(fbref_id="18bb7c11", fbref_url="/en/squads/18bb7c10/")
            db_session.commit()

    def test_team_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            team = Team(
                name="Arsenal",
                fbref_url="/en/squads/test/"
            )
            db_session.add(team)
            db_session.commit()

    def test_team_foreign_key_to_nation(self, db_session):
        """Test foreign key relationship to Nation."""
        nation = NationFactory()
        team = TeamFactory(nation=nation)
        db_session.commit()
        
        assert team.nation == nation

    def test_team_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        team = TeamFactory(
            nation=None,
            name=None,
            gender=None,
            fbref_url=None
        )
        db_session.commit()
        
        assert team.nation_id is None
        assert team.nation is None
        assert team.name is None
        assert team.gender is None
        assert team.fbref_url is None
