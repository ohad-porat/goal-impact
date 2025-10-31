"""Pydantic schemas for clubs endpoints."""

from typing import List, Optional
from pydantic import BaseModel


class NationBasic(BaseModel):
    """Basic nation information."""
    
    id: int
    name: str
    country_code: str


class ClubBasic(BaseModel):
    """Basic club information with average position."""
    
    id: int
    name: str
    avg_position: float


class ClubByNation(BaseModel):
    """Club group by nation."""
    
    nation: NationBasic
    clubs: List[ClubBasic]


class ClubsByNationResponse(BaseModel):
    """Response for listing clubs by nation."""
    
    nations: List[ClubByNation]


class NationDetailed(BaseModel):
    """Detailed nation information."""
    
    id: Optional[int]
    name: str
    country_code: Optional[str]


class ClubInfo(BaseModel):
    """Club information."""
    
    id: int
    name: str
    nation: NationDetailed


class SeasonInfoBasic(BaseModel):
    """Basic season information."""
    
    id: int
    start_year: int
    end_year: Optional[int]
    year_range: str


class CompetitionInfo(BaseModel):
    """Competition information."""
    
    id: int
    name: str
    tier: Optional[str]


class TeamStatsInfo(BaseModel):
    """Team statistics."""
    
    ranking: Optional[int]
    matches_played: Optional[int]
    wins: Optional[int]
    draws: Optional[int]
    losses: Optional[int]
    goals_for: Optional[int]
    goals_against: Optional[int]
    goal_difference: Optional[int]
    points: Optional[int]
    attendance: Optional[int]
    notes: Optional[str]


class SeasonStats(BaseModel):
    """Season statistics for a club."""
    
    season: SeasonInfoBasic
    competition: CompetitionInfo
    stats: TeamStatsInfo


class ClubDetailsResponse(BaseModel):
    """Response for club details endpoint."""
    
    club: ClubInfo
    seasons: List[SeasonStats]


class PlayerBasic(BaseModel):
    """Basic player information."""
    
    id: int
    name: str


class PlayerStatsBasic(BaseModel):
    """Player statistics for squad view."""
    
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


class SquadPlayer(BaseModel):
    """Player in squad with stats."""
    
    player: PlayerBasic
    stats: PlayerStatsBasic


class SeasonDisplay(BaseModel):
    """Season display information."""
    
    id: int
    start_year: int
    end_year: Optional[int]
    display_name: str


class CompetitionDisplay(BaseModel):
    """Competition display information."""
    
    id: Optional[int]
    name: str


class TeamSeasonSquadResponse(BaseModel):
    """Response for team season squad endpoint."""
    
    team: ClubInfo
    season: SeasonDisplay
    competition: CompetitionDisplay
    players: List[SquadPlayer]
