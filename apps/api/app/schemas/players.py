"""Pydantic schemas for players endpoints."""

from typing import List, Optional
from pydantic import BaseModel

from app.schemas.common import NationInfo


class PlayerInfo(BaseModel):
    """Player information."""
    
    id: int
    name: str
    nation: Optional[NationInfo]


class SeasonDisplay(BaseModel):
    """Season display information."""
    
    id: int
    start_year: int
    end_year: Optional[int]
    display_name: str


class TeamInfo(BaseModel):
    """Team information."""
    
    id: int
    name: str


class CompetitionInfo(BaseModel):
    """Competition information."""
    
    id: int
    name: str


class PlayerStats(BaseModel):
    """Player statistics."""
    
    matches_played: Optional[int]
    matches_started: Optional[int]
    total_minutes: Optional[int]
    minutes_divided_90: Optional[float]
    goals_scored: Optional[int]
    assists: Optional[int]
    total_goal_assists: Optional[int]
    non_pk_goals: Optional[int]
    pk_made: Optional[int]
    pk_attempted: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    goal_value: Optional[float]
    gv_avg: Optional[float]
    goal_per_90: Optional[float]
    assists_per_90: Optional[float]
    total_goals_assists_per_90: Optional[float]
    non_pk_goals_per_90: Optional[float]
    non_pk_goal_and_assists_per_90: Optional[float]


class SeasonData(BaseModel):
    """Season data for player."""
    
    season: SeasonDisplay
    team: TeamInfo
    competition: CompetitionInfo
    league_rank: Optional[int]
    stats: PlayerStats


class PlayerDetailsResponse(BaseModel):
    """Response for player details endpoint."""
    
    player: PlayerInfo
    seasons: List[SeasonData]
