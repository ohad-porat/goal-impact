"""Pydantic schemas for leagues endpoints."""

from pydantic import BaseModel

from app.schemas.players import SeasonDisplay


class LeagueSummary(BaseModel):
    """League summary information."""

    id: int
    name: str
    country: str
    gender: str | None
    tier: str | None
    available_seasons: str


class LeaguesListResponse(BaseModel):
    """Response for listing all leagues."""

    leagues: list[LeagueSummary]


class LeagueSeasonsResponse(BaseModel):
    """Response for league seasons endpoint."""

    seasons: list[SeasonDisplay]


class LeagueInfo(BaseModel):
    """League information."""

    id: int
    name: str
    country: str


class LeagueTableEntry(BaseModel):
    """League table entry."""

    position: int | None
    team_id: int
    team_name: str
    matches_played: int | None
    wins: int | None
    draws: int | None
    losses: int | None
    goals_for: int | None
    goals_against: int | None
    goal_difference: int | None
    points: int | None


class LeagueTableResponse(BaseModel):
    """Response for league table endpoint."""

    league: LeagueInfo
    season: SeasonDisplay
    table: list[LeagueTableEntry]
