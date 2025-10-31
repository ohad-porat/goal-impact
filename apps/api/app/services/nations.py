from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.competitions import Competition
from app.models.seasons import Season
from app.models.teams import Team
from app.models.team_stats import TeamStats
from app.models.players import Player
from app.models.player_stats import PlayerStats


def tier_order(tier: Optional[str]) -> int:
    if tier is None:
        return 99
    return {"1st": 1, "2nd": 2, "3rd": 3}.get(tier, 50)


def get_competitions_for_nation(db: Session, nation_id: int) -> List[Dict]:
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
        {
            "id": row.id,
            "name": row.name,
            "tier": row.tier,
            "season_count": int(row.season_count or 0),
            "has_seasons": (row.season_count or 0) > 0,
        }
        for row in rows
    ]
    data.sort(key=lambda x: (tier_order(x["tier"]), x["name"]))
    return data


def get_top_clubs_for_nation(db: Session, nation_id: int, limit: int = 10) -> List[Dict]:
    rows = (
        db.query(
            Team.id,
            Team.name,
            func.avg(TeamStats.ranking).label("avg_position"),
            func.count(TeamStats.id).label("stats_count"),
        )
        .join(TeamStats, TeamStats.team_id == Team.id)
        .join(Season, Season.id == TeamStats.season_id)
        .join(Competition, Competition.id == Season.competition_id)
        .filter(
            Team.nation_id == nation_id,
            Competition.tier == "1st",
            TeamStats.ranking.isnot(None),
        )
        .group_by(Team.id, Team.name)
        .order_by("avg_position", Team.name)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "avg_position": round(float(row.avg_position), 1) if row.avg_position is not None else None,
            "stats_count": int(row.stats_count or 0),
            "has_stats": (row.stats_count or 0) > 0,
        }
        for row in rows
    ]


def get_top_players_for_nation(db: Session, nation_id: int, limit: int = 20) -> List[Dict]:
    rows = (
        db.query(
            Player.id,
            Player.name,
            func.coalesce(func.sum(PlayerStats.goal_value), 0).label("total_goal_value"),
            func.count(PlayerStats.id).label("stats_count"),
        )
        .join(PlayerStats, PlayerStats.player_id == Player.id)
        .filter(Player.nation_id == nation_id)
        .group_by(Player.id, Player.name)
        .order_by(func.coalesce(func.sum(PlayerStats.goal_value), 0).desc(), Player.name)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "total_goal_value": float(row.total_goal_value or 0.0),
            "stats_count": int(row.stats_count or 0),
            "has_stats": (row.stats_count or 0) > 0,
        }
        for row in rows
    ]


