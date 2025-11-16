"""Unit tests for Player model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Player
from app.tests.utils.factories import PlayerFactory, NationFactory


class TestPlayerModel:
    """Test Player model functionality."""

    def test_create_player(self, db_session):
        """Test creating a player with all fields."""
        nation = NationFactory()
        player = PlayerFactory(
            name="Lionel Messi",
            fbref_id="d70ce98e",
            fbref_url="/en/players/d70ce98e/",
            nation=nation
        )
        db_session.commit()
        
        assert player.id is not None
        assert player.name == "Lionel Messi"
        assert player.fbref_id == "d70ce98e"
        assert player.fbref_url == "/en/players/d70ce98e/"
        assert player.nation_id == nation.id
        assert player.nation == nation

    def test_player_unique_fbref_id(self, db_session):
        """Test that fbref_id must be unique."""
        PlayerFactory(fbref_id="d70ce98e", fbref_url="/en/players/d70ce98e/")
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            PlayerFactory(fbref_id="d70ce98e", fbref_url="/en/players/d70ce98e2/")
            db_session.commit()

    def test_player_unique_fbref_url(self, db_session):
        """Test that fbref_url must be unique."""
        PlayerFactory(fbref_id="d70ce98e", fbref_url="/en/players/d70ce98e/")
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            PlayerFactory(fbref_id="d70ce98e2", fbref_url="/en/players/d70ce98e/")
            db_session.commit()

    def test_player_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        nation = NationFactory()
        
        with pytest.raises(IntegrityError):
            player = Player(
                name="Test Player",
                fbref_url="/en/players/test/",
                nation_id=nation.id
            )
            db_session.add(player)
            db_session.commit()

    def test_player_foreign_key_to_nation(self, db_session):
        """Test foreign key relationship to Nation."""
        nation = NationFactory()
        player = PlayerFactory(nation=nation)
        db_session.commit()
        
        assert player.nation == nation

    def test_player_optional_nation(self, db_session):
        """Test that nation_id can be null."""
        player = PlayerFactory(nation=None)
        db_session.commit()
        
        assert player.nation_id is None
        assert player.nation is None

    def test_player_cascade_behavior(self, db_session):
        """Test that deleting a nation doesn't cascade delete players."""
        nation = NationFactory()
        player = PlayerFactory(nation=nation)
        db_session.commit()
        
        player_id = player.id
        db_session.delete(nation)
        db_session.commit()
        
        player = db_session.query(Player).filter(Player.id == player_id).first()
        assert player is not None
