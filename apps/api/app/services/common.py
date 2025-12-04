"""Shared utility functions for services."""

from sqlalchemy import or_
from sqlalchemy.sql.elements import BooleanClauseList

from app.models.seasons import Season
from app.models.teams import Team
from app.schemas.clubs import ClubInfo, NationDetailed
from app.schemas.common import NationInfo


def format_season_display_name(start_year: int, end_year: int | None) -> str:
    """Format season year range for display."""
    if end_year and start_year != end_year:
        return f"{start_year}/{end_year}"
    return str(start_year)


def build_nation_info(nation) -> NationInfo | None:
    """Build NationInfo schema from a Nation model object or None."""
    if not nation:
        return None

    return NationInfo(id=nation.id, name=nation.name, country_code=nation.country_code)


def normalize_season_years(start_year: int, end_year: int) -> tuple[int, int]:
    """Normalize season years, mapping Brazilian single-year seasons to previous European format."""
    if start_year == end_year:
        return (start_year - 1, start_year)
    return (start_year, end_year)


def calculate_goal_value_avg(
    total_goal_value: float | None, total_goals: int | None
) -> float | None:
    """Calculate goal value average from total goal value and total goals."""
    if total_goals and total_goals > 0 and total_goal_value and total_goal_value > 0:
        return float(total_goal_value) / float(total_goals)
    return None


def build_season_filter_for_all_leagues(
    normalized_start: int, normalized_end: int
) -> BooleanClauseList:
    """Build season filter for all leagues query, matching both European and Brazilian seasons."""
    return or_(
        (Season.start_year == normalized_start) & (Season.end_year == normalized_end),
        (Season.start_year == normalized_end) & (Season.end_year == normalized_end),
    )


def build_club_info(team: Team) -> ClubInfo:
    """Build ClubInfo from Team model."""
    return ClubInfo(
        id=team.id,
        name=team.name,
        nation=NationDetailed(
            id=team.nation.id if team.nation else None,
            name=team.nation.name if team.nation else "Unknown",
            country_code=team.nation.country_code if team.nation else None,
        ),
    )
