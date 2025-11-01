"""Pydantic schemas for clubs endpoints."""

from typing import List, Optional
from pydantic import BaseModel
from app.schemas.players import PlayerStats, SeasonDisplay


class NationBasic(BaseModel):
    """Basic nation information."""
    
    id: int
    name: str
    country_code: str


class ClubSummary(BaseModel):
    """Club summary with average position."""
    
    id: int
    name: str
    avg_position: float


class ClubByNation(BaseModel):
    """Club group by nation."""
    
    nation: NationBasic
    clubs: List[ClubSummary]


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
    
    season: SeasonDisplay
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


class SquadPlayer(BaseModel):
    """Player in squad with stats."""
    
    player: PlayerBasic
    stats: PlayerStats


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


class GoalLogEntry(BaseModel):
    """Goal log entry with all relevant information."""
    
    date: str
    venue: str
    scorer: PlayerBasic
    opponent: ClubInfo
    minute: int
    score_before: str
    score_after: str
    goal_value: Optional[float]
    xg: Optional[float]
    post_shot_xg: Optional[float]
    assisted_by: Optional[PlayerBasic]


class TeamSeasonGoalLogResponse(BaseModel):
    """Response for team season goal log endpoint."""
    
    team: ClubInfo
    season: SeasonDisplay
    competition: CompetitionDisplay
    goals: List[GoalLogEntry]


class PlayerGoalLogEntry(BaseModel):
    """Goal log entry for player career (with team instead of scorer)."""
    
    date: str
    venue: str
    team: ClubInfo
    opponent: ClubInfo
    minute: int
    score_before: str
    score_after: str
    goal_value: Optional[float]
    xg: Optional[float]
    post_shot_xg: Optional[float]
    assisted_by: Optional[PlayerBasic]
    season_id: int
    season_display_name: str


class PlayerGoalLogResponse(BaseModel):
    """Response for player career goal log endpoint."""
    
    player: PlayerBasic
    goals: List[PlayerGoalLogEntry]
