"""Pydantic schemas for API responses."""

from .nations import (
    NationSummary,
    NationsListResponse,
    NationDetailsResponse,
    CompetitionSummary,
    PlayerSummary,
)
from .clubs import (
    ClubSummary,
    ClubByNation,
    ClubsByNationResponse,
    ClubDetailsResponse,
    SeasonStats,
    TeamSeasonSquadResponse,
)
from .leagues import (
    LeagueSummary,
    LeaguesListResponse,
    LeagueSeasonsResponse,
    LeagueTableEntry,
    LeagueTableResponse,
)
from .players import (
    PlayerDetailsResponse,
    SeasonData,
    PlayerStats,
    SeasonDisplay,
)

__all__ = [
    "NationSummary",
    "NationsListResponse",
    "NationDetailsResponse",
    "CompetitionSummary",
    "ClubSummary",
    "PlayerSummary",
    "ClubByNation",
    "ClubsByNationResponse",
    "ClubDetailsResponse",
    "SeasonStats",
    "TeamSeasonSquadResponse",
    "LeagueSummary",
    "LeaguesListResponse",
    "LeagueSeasonsResponse",
    "LeagueTableEntry",
    "LeagueTableResponse",
    "PlayerDetailsResponse",
    "SeasonData",
    "PlayerStats",
    "SeasonDisplay",
]
