"""Unit tests for common schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.common import NationInfo


class TestNationInfo:
    """Test NationInfo schema validation."""

    def test_all_fields_optional(self) -> None:
        """Test that all fields are optional."""
        nation = NationInfo()
        assert nation.id is None
        assert nation.name is None
        assert nation.country_code is None

    def test_creates_with_all_fields(self) -> None:
        """Test creating NationInfo with all fields."""
        nation = NationInfo(id=1, name="Argentina", country_code="AR")
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"

    def test_creates_with_partial_fields(self) -> None:
        """Test creating NationInfo with partial fields."""
        nation = NationInfo(id=1, name="Argentina")
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code is None

    def test_validates_id_type(self) -> None:
        """Test that id must be an integer."""
        with pytest.raises(ValidationError) as exc_info:
            NationInfo(id="not_an_int")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_validates_name_type(self) -> None:
        """Test that name must be a string."""
        with pytest.raises(ValidationError) as exc_info:
            NationInfo(name=12345)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_country_code_type(self) -> None:
        """Test that country_code must be a string."""
        with pytest.raises(ValidationError) as exc_info:
            NationInfo(country_code=123)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country_code",) for error in errors)

    def test_accepts_none_for_all_fields(self) -> None:
        """Test that None is accepted for all fields."""
        nation = NationInfo(id=None, name=None, country_code=None)
        assert nation.id is None
        assert nation.name is None
        assert nation.country_code is None

    def test_accepts_unicode_in_names(self) -> None:
        """Test that nation names with unicode characters work."""
        nation = NationInfo(id=1, name="Côte d'Ivoire", country_code="CI")
        assert nation.name == "Côte d'Ivoire"

    def test_accepts_zero_for_id(self) -> None:
        """Test that zero is a valid value for id."""
        nation = NationInfo(id=0, name="Test", country_code="XX")
        assert nation.id == 0

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        nation = NationInfo(id=1, name="Argentina", country_code="AR")
        data = nation.model_dump()
        assert data == {"id": 1, "name": "Argentina", "country_code": "AR"}

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Argentina", "country_code": "AR"}
        nation = NationInfo.model_validate(data)
        assert nation.id == 1
        assert nation.name == "Argentina"
        assert nation.country_code == "AR"

    def test_deserializes_with_none_values(self) -> None:
        """Test deserialization with None values."""
        data = {"id": None, "name": None, "country_code": None}
        nation = NationInfo.model_validate(data)
        assert nation.id is None
        assert nation.name is None
        assert nation.country_code is None
