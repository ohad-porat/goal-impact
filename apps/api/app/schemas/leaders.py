"""Schemas for leaders endpoints."""

from pydantic import BaseModel

from app.schemas.common import NationInfo


class CareerTotalsPlayer(BaseModel):
    """Player career totals information."""

    player_id: int
    player_name: str
    nation: NationInfo | None
    total_goal_value: float
    goal_value_avg: float
    total_goals: int
    total_matches: int


class CareerTotalsResponse(BaseModel):
    """Response for career totals leaders."""

    top_goal_value: list[CareerTotalsPlayer]


class BySeasonPlayer(BaseModel):
    """Player by season information."""

    player_id: int
    player_name: str
    clubs: str
    total_goal_value: float
    goal_value_avg: float
    total_goals: int
    total_matches: int


class BySeasonResponse(BaseModel):
    """Response for by season leaders."""

    top_goal_value: list[BySeasonPlayer]
