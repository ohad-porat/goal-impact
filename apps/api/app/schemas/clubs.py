"""Pydantic schemas for clubs endpoints."""

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
    clubs: list[ClubSummary]


class ClubsByNationResponse(BaseModel):
    """Response for listing clubs by nation."""

    nations: list[ClubByNation]


class NationDetailed(BaseModel):
    """Detailed nation information."""

    id: int | None = None
    name: str
    country_code: str | None = None


class ClubInfo(BaseModel):
    """Club information."""

    id: int
    name: str
    nation: NationDetailed


class CompetitionInfo(BaseModel):
    """Competition information."""

    id: int
    name: str
    tier: str | None = None


class TeamStatsInfo(BaseModel):
    """Team statistics."""

    ranking: int | None = None
    matches_played: int | None = None
    wins: int | None = None
    draws: int | None = None
    losses: int | None = None
    goals_for: int | None = None
    goals_against: int | None = None
    goal_difference: int | None = None
    points: int | None = None
    attendance: int | None = None
    notes: str | None = None


class SeasonStats(BaseModel):
    """Season statistics for a club."""

    season: SeasonDisplay
    competition: CompetitionInfo
    stats: TeamStatsInfo


class ClubDetailsResponse(BaseModel):
    """Response for club details endpoint."""

    club: ClubInfo
    seasons: list[SeasonStats]


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

    id: int | None = None
    name: str


class TeamSeasonSquadResponse(BaseModel):
    """Response for team season squad endpoint."""

    team: ClubInfo
    season: SeasonDisplay
    competition: CompetitionDisplay
    players: list[SquadPlayer]


class GoalLogEntry(BaseModel):
    """Goal log entry with all relevant information."""

    date: str
    venue: str
    scorer: PlayerBasic
    opponent: ClubInfo
    minute: int
    score_before: str
    score_after: str
    goal_value: float | None = None
    xg: float | None = None
    post_shot_xg: float | None = None
    assisted_by: PlayerBasic | None = None


class TeamSeasonGoalLogResponse(BaseModel):
    """Response for team season goal log endpoint."""

    team: ClubInfo
    season: SeasonDisplay
    competition: CompetitionDisplay
    goals: list[GoalLogEntry]


class PlayerGoalLogEntry(BaseModel):
    """Goal log entry for player career (with team instead of scorer)."""

    date: str
    venue: str
    team: ClubInfo
    opponent: ClubInfo
    minute: int
    score_before: str
    score_after: str
    goal_value: float | None = None
    xg: float | None = None
    post_shot_xg: float | None = None
    assisted_by: PlayerBasic | None = None
    season_id: int
    season_display_name: str


class PlayerGoalLogResponse(BaseModel):
    """Response for player career goal log endpoint."""

    player: PlayerBasic
    goals: list[PlayerGoalLogEntry]
