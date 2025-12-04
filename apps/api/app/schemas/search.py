"""Search-related schemas for API responses."""

from typing import Literal

from pydantic import BaseModel

SearchResultType = Literal["Player", "Club", "Competition", "Nation"]


class SearchResult(BaseModel):
    """Individual search result."""

    id: int
    name: str
    type: SearchResultType


class SearchResponse(BaseModel):
    """Search API response with results."""

    results: list[SearchResult]
