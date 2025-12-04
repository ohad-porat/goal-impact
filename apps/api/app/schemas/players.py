"""Pydantic schemas for players endpoints."""

from pydantic import BaseModel

from app.schemas.common import NationInfo


class PlayerInfo(BaseModel):
    """Player information."""

    id: int
    name: str
    nation: NationInfo | None


class SeasonDisplay(BaseModel):
    """Season display information."""

    id: int
    start_year: int
    end_year: int | None
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

    matches_played: int | None
    matches_started: int | None
    total_minutes: int | None
    minutes_divided_90: float | None
    goals_scored: int | None
    assists: int | None
    total_goal_assists: int | None
    non_pk_goals: int | None
    pk_made: int | None
    pk_attempted: int | None
    yellow_cards: int | None
    red_cards: int | None
    goal_value: float | None
    gv_avg: float | None
    goal_per_90: float | None
    assists_per_90: float | None
    total_goals_assists_per_90: float | None
    non_pk_goals_per_90: float | None
    non_pk_goal_and_assists_per_90: float | None


class SeasonData(BaseModel):
    """Season data for player."""

    season: SeasonDisplay
    team: TeamInfo
    competition: CompetitionInfo
    league_rank: int | None
    stats: PlayerStats


class PlayerDetailsResponse(BaseModel):
    """Response for player details endpoint."""

    player: PlayerInfo
    seasons: list[SeasonData]
