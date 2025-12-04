"""Pydantic schemas for API responses."""

from .clubs import (
    ClubByNation,
    ClubDetailsResponse,
    ClubsByNationResponse,
    ClubSummary,
    SeasonStats,
    TeamSeasonSquadResponse,
)
from .leagues import (
    LeagueSeasonsResponse,
    LeaguesListResponse,
    LeagueSummary,
    LeagueTableEntry,
    LeagueTableResponse,
)
from .nations import (
    CompetitionSummary,
    NationDetailsResponse,
    NationsListResponse,
    NationSummary,
    PlayerSummary,
)
from .players import (
    PlayerDetailsResponse,
    PlayerStats,
    SeasonData,
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
