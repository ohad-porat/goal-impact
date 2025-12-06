"""Nation-related business logic services."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.competitions import Competition
from app.models.nations import Nation
from app.models.player_stats import PlayerStats
from app.models.players import Player
from app.models.seasons import Season
from app.schemas.nations import CompetitionSummary, NationSummary, PlayerSummary

DEFAULT_TIER_ORDER = 50
UNKNOWN_TIER_ORDER = 99


def tier_order(tier: str | None) -> int:
    """Order tiers for sorting competitions.

    Args:
        tier: The tier string (e.g., "1st", "2nd", "3rd") or None

    Returns:
        Integer order value for sorting (lower = higher priority)
    """
    if tier is None:
        return UNKNOWN_TIER_ORDER
    return {"1st": 1, "2nd": 2, "3rd": 3}.get(tier, DEFAULT_TIER_ORDER)


def get_competitions_for_nation(db: Session, nation_id: int) -> list[CompetitionSummary]:
    """Get competitions for a specific nation.

    Args:
        db: Database session
        nation_id: ID of the nation to get competitions for

    Returns:
        List of CompetitionSummary objects, sorted by tier then name
    """
    rows = (
        db.query(
            Competition.id,
            Competition.name,
            Competition.tier,
            func.count(Season.id).label("season_count"),
        )
        .outerjoin(Season, Season.competition_id == Competition.id)
        .filter(Competition.nation_id == nation_id)
        .group_by(Competition.id, Competition.name, Competition.tier)
        .all()
    )

    data = [
        CompetitionSummary(
            id=row.id,
            name=row.name,
            tier=row.tier,
            season_count=int(row.season_count or 0),
            has_seasons=(row.season_count or 0) > 0,
        )
        for row in rows
    ]
    data.sort(key=lambda x: (tier_order(x.tier), x.name))
    return data


def get_all_nations_with_player_count(db: Session) -> list[NationSummary]:
    """Get all nations with their player counts, sorted by name."""
    nations_query = (
        db.query(
            Nation.id,
            Nation.name,
            Nation.country_code,
            Nation.governing_body,
            func.count(Player.id).label("player_count"),
        )
        .outerjoin(Player, Nation.id == Player.nation_id)
        .group_by(Nation.id, Nation.name, Nation.country_code, Nation.governing_body)
        .order_by(Nation.name)
        .all()
    )

    return [
        NationSummary(
            id=nation.id,
            name=nation.name,
            country_code=nation.country_code,
            governing_body=nation.governing_body or "N/A",
            player_count=nation.player_count,
        )
        for nation in nations_query
    ]


def get_top_players_for_nation(db: Session, nation_id: int, limit: int = 20) -> list[PlayerSummary]:
    """Get top players for a nation by total goal value.

    Args:
        db: Database session
        nation_id: ID of the nation to get players for
        limit: Maximum number of players to return (default: 20)

    Returns:
        List of PlayerSummary objects, sorted by total goal value descending
    """
    rows = (
        db.query(
            Player.id,
            Player.name,
            func.coalesce(func.sum(PlayerStats.goal_value), 0).label("total_goal_value"),
        )
        .join(PlayerStats, PlayerStats.player_id == Player.id)
        .filter(Player.nation_id == nation_id)
        .group_by(Player.id, Player.name)
        .order_by(func.coalesce(func.sum(PlayerStats.goal_value), 0).desc(), Player.name)
        .limit(limit)
        .all()
    )

    return [
        PlayerSummary(
            id=row.id,
            name=row.name,
            total_goal_value=float(row.total_goal_value or 0.0),
        )
        for row in rows
    ]
