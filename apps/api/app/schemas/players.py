"""Pydantic schemas for players endpoints."""

from pydantic import BaseModel

from app.schemas.common import NationInfo


class PlayerInfo(BaseModel):
    """Player information."""

    id: int
    name: str
    nation: NationInfo | None = None


class SeasonDisplay(BaseModel):
    """Season display information."""

    id: int
    start_year: int
    end_year: int | None = None
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

    matches_played: int | None = None
    matches_started: int | None = None
    total_minutes: int | None = None
    minutes_divided_90: float | None = None
    goals_scored: int | None = None
    assists: int | None = None
    total_goal_assists: int | None = None
    non_pk_goals: int | None = None
    pk_made: int | None = None
    pk_attempted: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None
    goal_value: float | None = None
    gv_avg: float | None = None
    goal_per_90: float | None = None
    assists_per_90: float | None = None
    total_goals_assists_per_90: float | None = None
    non_pk_goals_per_90: float | None = None
    non_pk_goal_and_assists_per_90: float | None = None


class SeasonData(BaseModel):
    """Season data for player."""

    season: SeasonDisplay
    team: TeamInfo
    competition: CompetitionInfo
    league_rank: int | None = None
    stats: PlayerStats


class CareerTotals(BaseModel):
    """Career totals for a player across all seasons."""

    total_goal_value: float
    goal_value_avg: float
    total_goals: int
    total_assists: int
    total_matches_played: int


class PlayerDetailsResponse(BaseModel):
    """Response for player details endpoint."""

    player: PlayerInfo
    seasons: list[SeasonData]
    career_totals: CareerTotals
