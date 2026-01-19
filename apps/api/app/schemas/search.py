"""Search-related schemas for API responses."""

from enum import Enum

from pydantic import BaseModel


class SearchType(str, Enum):
    """Enum for search result types."""

    PLAYER = "Player"
    CLUB = "Club"
    COMPETITION = "Competition"
    NATION = "Nation"


class SearchResult(BaseModel):
    """Individual search result."""

    id: int
    name: str
    type: SearchType


class SearchResponse(BaseModel):
    """Search API response with results."""

    results: list[SearchResult]
