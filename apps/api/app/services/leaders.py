"""Leaders-related business logic services."""

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import Nation, Player, PlayerStats, Season, Team
from app.schemas.leaders import AllSeasonsPlayer, BySeasonPlayer, CareerTotalsPlayer
from app.services.common import (
    build_nation_info,
    build_season_filter_for_all_leagues,
    calculate_goal_value_avg,
    format_season_display_name,
    normalize_season_years,
)


def _build_season_filter(ref_season: Season, league_id: int | None):
    """Build season filter for query.

    When league_id is None (all leagues), we normalize season years to handle
    Brazilian single-year seasons (e.g., 2023 -> 2022/2023) to match with
    European seasons. When filtering by a specific league, we use the exact
    season years since each league's seasons are already properly structured.

    Args:
        ref_season: Reference season to build filter from
        league_id: Optional league ID to filter by

    Returns:
        SQLAlchemy filter expression
    """
    if league_id is None:
        normalized_start, normalized_end = normalize_season_years(
            ref_season.start_year, ref_season.end_year
        )
        return build_season_filter_for_all_leagues(normalized_start, normalized_end)
    else:
        return (Season.start_year == ref_season.start_year) & (
            Season.end_year == ref_season.end_year
        )


def get_career_totals(
    db: Session, limit: int = 50, league_id: int | None = None
) -> list[CareerTotalsPlayer]:
    """Get top players by career goal value totals.

    Aggregates statistics across all seasons (or filtered by league).
    Only includes players with goal_value > 0.

    Args:
        db: Database session
        limit: Max players to return (default: 50)
        league_id: Optional league filter. None = all leagues.

    Returns:
        List of CareerTotalsPlayer sorted by total goal value descending.
    """
    query = (
        db.query(
            Player.id,
            Player.name,
            Player.nation_id,
            func.sum(PlayerStats.goal_value).label("total_goal_value"),
            func.sum(PlayerStats.goals_scored).label("total_goals"),
            func.sum(PlayerStats.matches_played).label("total_matches"),
        )
        .join(PlayerStats, Player.id == PlayerStats.player_id)
        .filter(PlayerStats.goal_value.isnot(None))
    )

    if league_id is not None:
        query = query.join(Season, PlayerStats.season_id == Season.id).filter(
            Season.competition_id == league_id
        )

    top_players_query = (
        query.group_by(Player.id, Player.name, Player.nation_id)
        .having(func.sum(PlayerStats.goal_value) > 0)
        .order_by(func.sum(PlayerStats.goal_value).desc())
        .limit(limit)
    )

    top_players_results = top_players_query.all()

    if not top_players_results:
        return []

    nation_ids = [row.nation_id for row in top_players_results if row.nation_id]

    nations_query = db.query(Nation).filter(Nation.id.in_(nation_ids))
    nations_results = nations_query.all()

    nations_dict = {nation.id: nation for nation in nations_results}

    def build_player(row) -> CareerTotalsPlayer:
        nation = build_nation_info(nations_dict.get(row.nation_id)) if row.nation_id else None

        goal_value_avg = calculate_goal_value_avg(row.total_goal_value, row.total_goals)

        return CareerTotalsPlayer(
            player_id=row.id,
            player_name=row.name,
            nation=nation,
            total_goal_value=round(row.total_goal_value, 2) if row.total_goal_value else 0.0,
            goal_value_avg=round(goal_value_avg, 2) if goal_value_avg else 0.0,
            total_goals=int(row.total_goals) if row.total_goals else 0,
            total_matches=int(row.total_matches) if row.total_matches else 0,
        )

    return [build_player(row) for row in top_players_results]


def get_by_season(
    db: Session, season_id: int, limit: int = 50, league_id: int | None = None
) -> list[BySeasonPlayer]:
    """Get top players by goal value for a specific season.

    When league_id is None, normalizes Brazilian seasons (2023 -> 2022/2023) to
    match European seasons across all leagues. Aggregates stats across all teams
    per player, including comma-separated club list.

    Args:
        db: Database session
        season_id: Reference season ID
        limit: Max players to return (default: 50)
        league_id: Optional league filter. None = cross-league with normalization.

    Returns:
        List of BySeasonPlayer sorted by total goal value descending.
    """
    ref_season = db.query(Season).filter(Season.id == season_id).first()
    if not ref_season:
        return []

    season_filter = _build_season_filter(ref_season, league_id)

    player_stats = (
        db.query(
            PlayerStats.player_id,
            func.sum(PlayerStats.goal_value).label("total_goal_value"),
            func.sum(PlayerStats.goals_scored).label("total_goals"),
            func.sum(PlayerStats.matches_played).label("total_matches"),
        )
        .join(Season, PlayerStats.season_id == Season.id)
        .filter(season_filter)
        .filter(PlayerStats.goal_value.isnot(None))
        .group_by(PlayerStats.player_id)
        .having(func.sum(PlayerStats.goal_value) > 0)
    )

    if league_id is not None:
        player_stats = player_stats.filter(Season.competition_id == league_id)

    player_stats = player_stats.subquery()

    top_players_query = (
        db.query(
            player_stats.c.player_id,
            Player.name.label("player_name"),
            player_stats.c.total_goal_value,
            player_stats.c.total_goals,
            player_stats.c.total_matches,
        )
        .join(Player, player_stats.c.player_id == Player.id)
        .order_by(player_stats.c.total_goal_value.desc())
        .limit(limit)
    )

    top_players_results = top_players_query.all()

    if not top_players_results:
        return []

    top_player_ids = [row.player_id for row in top_players_results]

    team_names_query = (
        db.query(PlayerStats.player_id, func.string_agg(Team.name, ",").label("team_names"))
        .join(Season, PlayerStats.season_id == Season.id)
        .join(Team, PlayerStats.team_id == Team.id)
        .filter(season_filter)
        .filter(PlayerStats.player_id.in_(top_player_ids))
    )

    if league_id is not None:
        team_names_query = team_names_query.filter(Season.competition_id == league_id)

    team_names_results = team_names_query.group_by(PlayerStats.player_id).all()

    team_names_dict = {row.player_id: row.team_names for row in team_names_results}

    def build_by_season_player(row) -> BySeasonPlayer:
        team_names = team_names_dict.get(row.player_id)
        club_names = []
        if team_names:
            club_names = sorted(set(team_names.split(",")))
        clubs_display = ", ".join(club_names) if club_names else "-"

        goal_value_avg = calculate_goal_value_avg(row.total_goal_value, row.total_goals)

        return BySeasonPlayer(
            player_id=row.player_id,
            player_name=row.player_name,
            clubs=clubs_display,
            total_goal_value=round(row.total_goal_value, 2) if row.total_goal_value else 0.0,
            goal_value_avg=round(goal_value_avg, 2) if goal_value_avg else 0.0,
            total_goals=int(row.total_goals) if row.total_goals else 0,
            total_matches=int(row.total_matches) if row.total_matches else 0,
        )

    return [build_by_season_player(row) for row in top_players_results]


def get_all_seasons(
    db: Session, limit: int = 50, league_id: int | None = None
) -> list[AllSeasonsPlayer]:
    """Get top player-seasons by goal value across all seasons.

    Groups by (player_id, season_id) and returns top results sorted by
    total_goal_value descending, then goal_value_avg descending.

    Args:
        db: Database session
        limit: Max results to return (default: 50)
        league_id: Optional league filter. None = all leagues.

    Returns:
        List of AllSeasonsPlayer sorted by total goal value descending.
    """
    player_stats = (
        db.query(
            PlayerStats.player_id,
            PlayerStats.season_id,
            func.sum(PlayerStats.goal_value).label("total_goal_value"),
            func.sum(PlayerStats.goals_scored).label("total_goals"),
            func.sum(PlayerStats.matches_played).label("total_matches"),
        )
        .join(Season, PlayerStats.season_id == Season.id)
        .filter(PlayerStats.goal_value.isnot(None))
        .group_by(PlayerStats.player_id, PlayerStats.season_id)
        .having(func.sum(PlayerStats.goal_value) > 0)
    )

    if league_id is not None:
        player_stats = player_stats.filter(Season.competition_id == league_id)

    player_stats = player_stats.subquery()

    top_players_query = (
        db.query(
            player_stats.c.player_id,
            player_stats.c.season_id,
            Player.name.label("player_name"),
            player_stats.c.total_goal_value,
            player_stats.c.total_goals,
            player_stats.c.total_matches,
        )
        .join(Player, player_stats.c.player_id == Player.id)
        .order_by(
            player_stats.c.total_goal_value.desc(),
            (player_stats.c.total_goal_value / func.nullif(player_stats.c.total_goals, 0)).desc(),
        )
        .limit(limit)
    )

    top_players_results = top_players_query.all()

    if not top_players_results:
        return []

    season_ids = [row.season_id for row in top_players_results]
    seasons_query = db.query(Season).filter(Season.id.in_(season_ids))
    seasons_results = seasons_query.all()
    seasons_dict = {season.id: season for season in seasons_results}

    top_player_season_pairs = [(row.player_id, row.season_id) for row in top_players_results]

    if not top_player_season_pairs:
        return []

    conditions = [
        (PlayerStats.player_id == player_id) & (PlayerStats.season_id == season_id)
        for player_id, season_id in top_player_season_pairs
    ]
    team_names_query = (
        db.query(
            PlayerStats.player_id,
            PlayerStats.season_id,
            func.string_agg(Team.name, ",").label("team_names"),
        )
        .join(Team, PlayerStats.team_id == Team.id)
        .filter(or_(*conditions))
        .group_by(PlayerStats.player_id, PlayerStats.season_id)
    )

    if league_id is not None:
        team_names_query = team_names_query.join(Season, PlayerStats.season_id == Season.id).filter(
            Season.competition_id == league_id
        )

    team_names_results = team_names_query.all()
    team_names_dict = {(row.player_id, row.season_id): row.team_names for row in team_names_results}

    def build_all_seasons_player(row) -> AllSeasonsPlayer:
        season = seasons_dict.get(row.season_id)
        season_display_name = (
            format_season_display_name(season.start_year, season.end_year) if season else "Unknown"
        )

        team_names = team_names_dict.get((row.player_id, row.season_id))
        club_names = []
        if team_names:
            club_names = sorted(set(team_names.split(",")))
        clubs_display = ", ".join(club_names) if club_names else "-"

        goal_value_avg = calculate_goal_value_avg(row.total_goal_value, row.total_goals)

        return AllSeasonsPlayer(
            player_id=row.player_id,
            player_name=row.player_name,
            season_id=row.season_id,
            season_display_name=season_display_name,
            clubs=clubs_display,
            total_goal_value=round(row.total_goal_value, 2) if row.total_goal_value else 0.0,
            goal_value_avg=round(goal_value_avg, 2) if goal_value_avg else 0.0,
            total_goals=int(row.total_goals) if row.total_goals else 0,
            total_matches=int(row.total_matches) if row.total_matches else 0,
        )

    return [build_all_seasons_player(row) for row in top_players_results]
