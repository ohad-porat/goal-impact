"""Pydantic schemas for API responses."""

from .nations import (
    NationSummary,
    NationsListResponse,
    NationDetailsResponse,
    CompetitionSummary,
    ClubSummary,
    PlayerSummary,
)
from .clubs import (
    ClubByNation,
    ClubsByNationResponse,
    ClubDetailsResponse,
    SeasonStats,
    TeamSeasonSquadResponse,
    PlayerStatsBasic,
)
from .leagues import (
    LeagueSummary,
    LeaguesListResponse,
    SeasonInfo,
    LeagueSeasonsResponse,
    LeagueTableEntry,
    LeagueTableResponse,
)
from .players import (
    PlayerDetailsResponse,
    SeasonData,
    PlayerStatsDetailed,
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
    "PlayerStatsBasic",
    "LeagueSummary",
    "LeaguesListResponse",
    "SeasonInfo",
    "LeagueSeasonsResponse",
    "LeagueTableEntry",
    "LeagueTableResponse",
    "PlayerDetailsResponse",
    "SeasonData",
    "PlayerStatsDetailed",
]
