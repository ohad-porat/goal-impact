"""Shared utility functions for services."""

from typing import Optional
from app.schemas.common import NationInfo


def format_season_display_name(start_year: int, end_year: Optional[int]) -> str:
    """Format season year range for display."""
    if end_year and start_year != end_year:
        return f"{start_year}/{end_year}"
    return str(start_year)


def build_nation_info(nation) -> Optional[NationInfo]:
    """Build NationInfo schema from a Nation model object or None."""
    if not nation:
        return None
    
    return NationInfo(
        id=nation.id,
        name=nation.name,
        country_code=nation.country_code
    )
