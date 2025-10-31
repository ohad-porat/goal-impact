"""Pydantic schemas for nations endpoints."""

from typing import List, Optional
from pydantic import BaseModel


class NationSummary(BaseModel):
    """Nation summary with player count."""
    
    id: int
    name: str
    country_code: str
    governing_body: str
    player_count: int


class NationsListResponse(BaseModel):
    """Response for listing all nations."""
    
    nations: List[NationSummary]


class NationInfo(BaseModel):
    """Basic nation information."""
    
    id: int
    name: str
    country_code: str
    governing_body: str


class CompetitionSummary(BaseModel):
    """Competition summary for nation details."""
    
    id: int
    name: str
    tier: Optional[str]
    season_count: int
    has_seasons: bool


class ClubSummary(BaseModel):
    """Club summary for nation details."""
    
    id: int
    name: str
    avg_position: Optional[float]
    stats_count: int
    has_stats: bool


class PlayerSummary(BaseModel):
    """Player summary for nation details."""
    
    id: int
    name: str
    total_goal_value: float
    stats_count: int
    has_stats: bool


class NationDetailsResponse(BaseModel):
    """Response for nation details endpoint."""
    
    nation: NationInfo
    competitions: List[CompetitionSummary]
    clubs: List[ClubSummary]
    players: List[PlayerSummary]
