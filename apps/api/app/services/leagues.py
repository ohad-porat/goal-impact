"""League-related business logic services."""

from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app.models.competitions import Competition
from app.models.nations import Nation
from app.models.seasons import Season
from app.models.team_stats import TeamStats
from app.schemas.leagues import (
    LeagueInfo,
    LeagueSummary,
    LeagueTableEntry,
)
from app.schemas.players import SeasonDisplay
from app.services.common import format_season_display_name
from app.services.nations import tier_order


def format_season_range(seasons: list[Season]) -> str:
    """Format season range string for display.

    Creates a human-readable range string from a list of seasons, showing
    the first and last season years. Handles both single-year and multi-year
    season formats.

    Args:
        seasons: List of Season objects to format

    Returns:
        Formatted string like "2020/2021 - 2023/2024" or "2020 - 2023" for
        single-year seasons. Returns "No seasons available" if list is empty.
    """
    if not seasons:
        return "No seasons available"

    sorted_seasons = sorted(seasons, key=lambda season: season.start_year)
    first_season = sorted_seasons[0]
    last_season = sorted_seasons[-1]

    if (
        first_season.start_year == first_season.end_year
        and last_season.start_year == last_season.end_year
    ):
        return f"{first_season.start_year} - {last_season.start_year}"
    else:
        first_range = format_season_display_name(first_season.start_year, first_season.end_year)
        last_range = format_season_display_name(last_season.start_year, last_season.end_year)
        return f"{first_range} - {last_range}"


def get_all_leagues_with_season_ranges(db: Session) -> list[LeagueSummary]:
    """Get all leagues with season ranges.

    Args:
        db: Database session

    Returns:
        List of LeagueSummary sorted by country and tier.
    """
    competitions = (
        db.query(Competition)
        .join(Nation)
        .options(joinedload(Competition.seasons), joinedload(Competition.nation))
        .all()
    )

    leagues_data = []
    for competition in competitions:
        available_seasons = format_season_range(competition.seasons)

        leagues_data.append(
            LeagueSummary(
                id=competition.id,
                name=competition.name,
                country=competition.nation.name if competition.nation else "Unknown",
                gender=competition.gender,
                tier=competition.tier,
                available_seasons=available_seasons,
            )
        )

    leagues_data.sort(key=lambda x: (x.country, tier_order(x.tier)))

    return leagues_data


def get_league_seasons(db: Session, league_id: int) -> list[SeasonDisplay]:
    """Get seasons for a league, sorted by start_year descending.

    Args:
        db: Database session
        league_id: ID of the league/competition

    Returns:
        List of SeasonDisplay objects, sorted by start_year descending (most recent first)
    """
    seasons = db.query(Season).filter(Season.competition_id == league_id).all()

    seasons_data = [
        SeasonDisplay(
            id=season.id,
            start_year=season.start_year,
            end_year=season.end_year,
            display_name=format_season_display_name(season.start_year, season.end_year),
        )
        for season in seasons
    ]

    seasons_data.sort(key=lambda x: x.start_year, reverse=True)
    return seasons_data


def get_all_unique_seasons(db: Session) -> list[SeasonDisplay]:
    """Get all unique seasons grouped by logical period.

    Normalizes Brazilian single-year seasons (2023) to European format (2022/2023)
    for grouping. Uses window functions to select one season per normalized period,
    preferring multi-year over single-year seasons.

    Args:
        db: Database session

    Returns:
        List of SeasonDisplay objects, sorted by start year descending.
    """
    normalized_start = case(
        (Season.start_year == Season.end_year, Season.start_year - 1), else_=Season.start_year
    ).label("normalized_start")

    normalized_end = Season.end_year.label("normalized_end")

    preferred_priority = case((Season.start_year != Season.end_year, 1), else_=2).label(
        "preferred_priority"
    )

    ranked_seasons = db.query(
        Season.id,
        normalized_start,
        normalized_end,
        func.row_number()
        .over(
            partition_by=[normalized_start, normalized_end],
            order_by=[preferred_priority.asc(), Season.id.asc()],
        )
        .label("rank"),
    ).subquery()

    unique_seasons = (
        db.query(
            ranked_seasons.c.id, ranked_seasons.c.normalized_start, ranked_seasons.c.normalized_end
        )
        .filter(ranked_seasons.c.rank == 1)
        .order_by(ranked_seasons.c.normalized_start.desc())
        .all()
    )

    seen_display_names = set()
    seasons_data = []

    for season_row in unique_seasons:
        display_name = format_season_display_name(
            season_row.normalized_start, season_row.normalized_end
        )

        if display_name not in seen_display_names:
            seen_display_names.add(display_name)
            seasons_data.append(
                SeasonDisplay(
                    id=season_row.id,
                    start_year=season_row.normalized_start,
                    end_year=season_row.normalized_end,
                    display_name=display_name,
                )
            )

    return seasons_data


def get_league_table_for_season(
    db: Session, league_id: int, season_id: int
) -> tuple[LeagueInfo | None, SeasonDisplay | None, list[LeagueTableEntry]]:
    """Get league table for a league and season.

    Retrieves the complete league standings (table) for a specific league and season,
    including all team statistics: matches played, wins, draws, losses, goals, points, etc.

    Args:
        db: Database session
        league_id: ID of the league/competition
        season_id: ID of the season

    Returns:
        Tuple containing:
        - LeagueInfo or None if league not found
        - SeasonDisplay or None if season not found or doesn't belong to league
        - List of LeagueTableEntry objects, sorted by ranking (position)
    """
    competition = (
        db.query(Competition)
        .options(joinedload(Competition.nation))
        .filter(Competition.id == league_id)
        .first()
    )
    if not competition:
        return None, None, []

    season = (
        db.query(Season).filter(Season.id == season_id, Season.competition_id == league_id).first()
    )
    if not season:
        league_info = LeagueInfo(
            id=competition.id,
            name=competition.name,
            country=competition.nation.name if competition.nation else "Unknown",
        )
        return league_info, None, []

    team_stats = (
        db.query(TeamStats)
        .options(joinedload(TeamStats.team))
        .filter(TeamStats.season_id == season_id)
        .order_by(TeamStats.ranking)
        .all()
    )

    table_data = [
        LeagueTableEntry(
            position=team_stat.ranking,
            team_id=team_stat.team.id,
            team_name=team_stat.team.name,
            matches_played=team_stat.matches_played,
            wins=team_stat.wins,
            draws=team_stat.draws,
            losses=team_stat.losses,
            goals_for=team_stat.goals_for,
            goals_against=team_stat.goals_against,
            goal_difference=team_stat.goal_difference,
            points=team_stat.points,
        )
        for team_stat in team_stats
    ]

    league_info = LeagueInfo(
        id=competition.id,
        name=competition.name,
        country=competition.nation.name if competition.nation else "Unknown",
    )

    season_info = SeasonDisplay(
        id=season.id,
        start_year=season.start_year,
        end_year=season.end_year,
        display_name=format_season_display_name(season.start_year, season.end_year),
    )

    return league_info, season_info, table_data
