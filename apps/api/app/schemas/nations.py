"""Pydantic schemas for nations endpoints."""

from pydantic import BaseModel

from app.schemas.clubs import ClubSummary


class NationSummary(BaseModel):
    """Nation summary with player count."""

    id: int
    name: str
    country_code: str
    governing_body: str
    player_count: int


class NationsListResponse(BaseModel):
    """Response for listing all nations."""

    nations: list[NationSummary]


class NationDetails(BaseModel):
    """Detailed nation information with governing body."""

    id: int
    name: str
    country_code: str
    governing_body: str


class CompetitionSummary(BaseModel):
    """Competition summary for nation details."""

    id: int
    name: str
    tier: str | None
    season_count: int
    has_seasons: bool


class PlayerSummary(BaseModel):
    """Player summary for nation details."""

    id: int
    name: str
    total_goal_value: float


class NationDetailsResponse(BaseModel):
    """Response for nation details endpoint."""

    nation: NationDetails
    competitions: list[CompetitionSummary]
    clubs: list[ClubSummary]
    players: list[PlayerSummary]
