"""Command line interface parser for FBRef scraper."""

import argparse
from datetime import date, datetime


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="FBRef scraper with initial, daily, and seasonal modes"
    )

    parser.add_argument(
        "--mode",
        choices=["initial", "daily", "seasonal"],
        default="initial",
        help="Scraping mode: initial (full scrape), daily (update stats), or seasonal (handle new seasons)",
    )

    parser.add_argument(
        "--days", type=int, default=1, help="Number of days back for incremental mode (default: 1)"
    )

    parser.add_argument("--from-date", type=str, help="Custom start date (YYYY-MM-DD format)")

    parser.add_argument("--to-date", type=str, help="Custom end date (YYYY-MM-DD format)")

    parser.add_argument(
        "--nations", type=str, help="Comma-separated nation names (overrides config)"
    )

    parser.add_argument("--from-year", type=int, help="Custom start year")

    parser.add_argument("--to-year", type=int, help="Custom end year")

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from where the last run left off (if progress files exist)",
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if individual items fail",
    )

    return parser.parse_args()


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as err:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.") from err


def parse_nations(nations_str: str) -> list[str]:
    """Parse comma-separated nations string."""
    return [nation.strip() for nation in nations_str.split(",")]
