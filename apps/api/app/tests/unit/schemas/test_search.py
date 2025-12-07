"""Unit tests for search schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.search import SearchResponse, SearchResult, SearchResultType


class TestSearchResult:
    """Test SearchResult schema validation."""

    def test_creates_with_required_fields(self) -> None:
        """Test creating SearchResult with required fields."""
        result = SearchResult(id=1, name="Lionel Messi", type="Player")
        assert result.id == 1
        assert result.name == "Lionel Messi"
        assert result.type == "Player"

    def test_accepts_all_valid_types(self) -> None:
        """Test that all valid SearchResultType values are accepted."""
        valid_types: list[SearchResultType] = ["Player", "Club", "Competition", "Nation"]
        for result_type in valid_types:
            result = SearchResult(id=1, name="Test", type=result_type)
            assert result.type == result_type

    def test_requires_id(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(name="Lionel Messi", type="Player")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_requires_name(self) -> None:
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(id=1, type="Player")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_requires_type(self) -> None:
        """Test that type is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(id=1, name="Lionel Messi")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("type",) for error in errors)

    def test_validates_id_type(self) -> None:
        """Test that id must be an integer."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(id="not_int", name="Lionel Messi", type="Player")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_validates_name_type(self) -> None:
        """Test that name must be a string."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(id=1, name=123, type="Player")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_validates_type_literal(self) -> None:
        """Test that type must be a valid SearchResultType."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(id=1, name="Lionel Messi", type="InvalidType")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("type",) for error in errors)

    def test_accepts_unicode_in_names(self) -> None:
        """Test that search result names with unicode characters work."""
        result = SearchResult(id=1, name="José Mourinho", type="Player")
        assert result.name == "José Mourinho"

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        result = SearchResult(id=1, name="Lionel Messi", type="Player")
        data = result.model_dump()
        assert data == {"id": 1, "name": "Lionel Messi", "type": "Player"}

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"id": 1, "name": "Lionel Messi", "type": "Player"}
        result = SearchResult.model_validate(data)
        assert result.id == 1
        assert result.name == "Lionel Messi"
        assert result.type == "Player"


class TestSearchResponse:
    """Test SearchResponse schema validation."""

    def test_creates_with_empty_list(self) -> None:
        """Test creating SearchResponse with empty list."""
        response = SearchResponse(results=[])
        assert response.results == []

    def test_creates_with_results(self) -> None:
        """Test creating SearchResponse with results."""
        result1 = SearchResult(id=1, name="Lionel Messi", type="Player")
        result2 = SearchResult(id=2, name="Barcelona", type="Club")
        response = SearchResponse(results=[result1, result2])
        assert len(response.results) == 2
        assert response.results[0].name == "Lionel Messi"
        assert response.results[1].name == "Barcelona"

    def test_requires_results(self) -> None:
        """Test that results is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResponse()
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("results",) for error in errors)

    def test_validates_list_type(self) -> None:
        """Test that results must be a list."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResponse(results="not_a_list")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("results",) for error in errors)

    def test_validates_list_items(self) -> None:
        """Test that list items must be valid SearchResult objects."""
        with pytest.raises(ValidationError) as exc_info:
            SearchResponse(results=[{"invalid": "data"}])
        errors = exc_info.value.errors()
        # Should have validation errors for missing required fields
        assert len(errors) > 0

    def test_serializes_to_dict(self) -> None:
        """Test serialization to dictionary."""
        result = SearchResult(id=1, name="Lionel Messi", type="Player")
        response = SearchResponse(results=[result])
        data = response.model_dump()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Lionel Messi"

    def test_deserializes_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "results": [
                {"id": 1, "name": "Lionel Messi", "type": "Player"},
                {"id": 2, "name": "Barcelona", "type": "Club"},
            ]
        }
        response = SearchResponse.model_validate(data)
        assert len(response.results) == 2
        assert response.results[0].name == "Lionel Messi"
        assert response.results[1].name == "Barcelona"
