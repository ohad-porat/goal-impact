"""Pydantic schemas for leagues endpoints."""

from typing import List, Optional
from pydantic import BaseModel


class LeagueSummary(BaseModel):
    """League summary information."""
    
    id: int
    name: str
    country: str
    gender: Optional[str]
    tier: Optional[str]
    available_seasons: str


class LeaguesListResponse(BaseModel):
    """Response for listing all leagues."""
    
    leagues: List[LeagueSummary]


class SeasonInfo(BaseModel):
    """Season information."""
    
    id: int
    start_year: int
    end_year: Optional[int]
    display_name: str


class LeagueSeasonsResponse(BaseModel):
    """Response for league seasons endpoint."""
    
    seasons: List[SeasonInfo]


class LeagueInfo(BaseModel):
    """League information."""
    
    id: int
    name: str
    country: str


class LeagueTableEntry(BaseModel):
    """League table entry."""
    
    position: Optional[int]
    team_id: int
    team_name: str
    matches_played: Optional[int]
    wins: Optional[int]
    draws: Optional[int]
    losses: Optional[int]
    goals_for: Optional[int]
    goals_against: Optional[int]
    goal_difference: Optional[int]
    points: Optional[int]


class LeagueTableResponse(BaseModel):
    """Response for league table endpoint."""
    
    league: LeagueInfo
    season: SeasonInfo
    table: List[LeagueTableEntry]
