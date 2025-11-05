"""Search-related schemas for API responses."""

from pydantic import BaseModel
from typing import Literal


SearchResultType = Literal["Player", "Club", "Competition", "Nation"]


class SearchResult(BaseModel):
    """Individual search result."""
    id: int
    name: str
    type: SearchResultType


class SearchResponse(BaseModel):
    """Search API response with results."""
    results: list[SearchResult]

