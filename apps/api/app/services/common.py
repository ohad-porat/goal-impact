"""Shared utility functions for services."""

from typing import Optional


def format_season_display_name(start_year: int, end_year: Optional[int]) -> str:
    """Format season year range for display."""
    if end_year and start_year != end_year:
        return f"{start_year}/{end_year}"
    return str(start_year)
