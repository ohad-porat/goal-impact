"""Pydantic schemas for home page endpoints."""

from pydantic import BaseModel


class RecentGoalPlayer(BaseModel):
    """Basic player information for recent goals."""

    id: int
    name: str


class RecentGoalMatch(BaseModel):
    """Match information for recent goals."""

    home_team: str
    away_team: str
    date: str


class RecentImpactGoal(BaseModel):
    """Recent impact goal entry."""

    match: RecentGoalMatch
    scorer: RecentGoalPlayer
    minute: int
    goal_value: float
    score_before: str
    score_after: str


class RecentImpactGoalsResponse(BaseModel):
    """Response for recent impact goals."""

    goals: list[RecentImpactGoal]
