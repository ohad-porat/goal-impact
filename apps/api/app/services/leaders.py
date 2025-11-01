"""Leaders-related business logic services."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Player, PlayerStats, Nation, Season
from app.schemas.leaders import CareerTotalsPlayer
from app.services.common import build_nation_info


def get_career_totals(db: Session, limit: int = 50, league_id: Optional[int] = None) -> List[CareerTotalsPlayer]:
    """Get top players by career goal value totals, optionally filtered by league."""
    query = (
        db.query(
            Player.id,
            Player.name,
            Player.nation_id,
            func.sum(PlayerStats.goal_value).label('total_goal_value'),
            func.sum(PlayerStats.goals_scored).label('total_goals'),
            func.sum(PlayerStats.matches_played).label('total_matches')
        )
        .join(PlayerStats, Player.id == PlayerStats.player_id)
        .filter(PlayerStats.goal_value.isnot(None))
    )
    
    if league_id is not None:
        query = query.join(Season, PlayerStats.season_id == Season.id).filter(Season.competition_id == league_id)
    
    career_stats = (
        query
        .group_by(Player.id, Player.name, Player.nation_id)
        .having(func.sum(PlayerStats.goal_value) > 0)
        .subquery()
    )
    
    top_goal_value_query = (
        db.query(
            career_stats.c.id,
            career_stats.c.name,
            career_stats.c.nation_id,
            career_stats.c.total_goal_value,
            career_stats.c.total_goals,
            career_stats.c.total_matches
        )
        .order_by(career_stats.c.total_goal_value.desc())
        .limit(limit)
    )
    
    top_goal_value_results = top_goal_value_query.all()
    
    nation_ids = [row.nation_id for row in top_goal_value_results if row.nation_id]
    nations_dict = {}
    if nation_ids:
        nations = db.query(Nation).filter(Nation.id.in_(nation_ids)).all()
        nations_dict = {nation.id: nation for nation in nations}
    
    def build_player(row, nations_dict) -> CareerTotalsPlayer:
        nation_obj = None
        if row.nation_id and row.nation_id in nations_dict:
            nation_obj = nations_dict[row.nation_id]
        nation = build_nation_info(nation_obj)
        
        goal_value_avg = None
        if row.total_goals and row.total_goals > 0 and row.total_goal_value and row.total_goal_value > 0:
            goal_value_avg = float(row.total_goal_value) / float(row.total_goals)
        
        return CareerTotalsPlayer(
            player_id=row.id,
            player_name=row.name,
            nation=nation,
            total_goal_value=round(row.total_goal_value, 2) if row.total_goal_value else 0.0,
            goal_value_avg=round(goal_value_avg, 2) if goal_value_avg else 0.0,
            total_goals=int(row.total_goals) if row.total_goals else 0,
            total_matches=int(row.total_matches) if row.total_matches else 0
        )
    
    top_goal_value = [build_player(row, nations_dict) for row in top_goal_value_results]
    
    return top_goal_value
