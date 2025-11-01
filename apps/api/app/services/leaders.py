"""Leaders-related business logic services."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Player, PlayerStats, Nation, Season, Team
from app.schemas.leaders import CareerTotalsPlayer, BySeasonPlayer
from app.services.common import build_nation_info, normalize_season_years, calculate_goal_value_avg, build_season_filter_for_all_leagues


def _build_season_filter(ref_season: Season, league_id: Optional[int]):
    """Build season filter for query, handling grouped seasons when league_id is None."""
    if league_id is None:
        normalized_start, normalized_end = normalize_season_years(ref_season.start_year, ref_season.end_year)
        return build_season_filter_for_all_leagues(normalized_start, normalized_end)
    else:
        return (Season.start_year == ref_season.start_year) & (Season.end_year == ref_season.end_year)


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
        
        goal_value_avg = calculate_goal_value_avg(row.total_goal_value, row.total_goals)
        
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


def get_by_season(
    db: Session, 
    season_id: int, 
    limit: int = 50, 
    league_id: Optional[int] = None
) -> List[BySeasonPlayer]:
    """Get top players by goal value for a specific season, optionally filtered by league."""
    ref_season = db.query(Season).filter(Season.id == season_id).first()
    if not ref_season:
        return []
    
    season_filter = _build_season_filter(ref_season, league_id)
    
    query = (
        db.query(
            PlayerStats.player_id,
            func.sum(PlayerStats.goal_value).label('total_goal_value'),
            func.sum(PlayerStats.goals_scored).label('total_goals'),
            func.sum(PlayerStats.matches_played).label('total_matches')
        )
        .join(Season, PlayerStats.season_id == Season.id)
        .filter(season_filter)
        .filter(PlayerStats.goal_value.isnot(None))
    )
    
    if league_id is not None:
        query = query.filter(Season.competition_id == league_id)
    
    player_stats = (
        query
        .group_by(PlayerStats.player_id)
        .having(func.sum(PlayerStats.goal_value) > 0)
        .subquery()
    )
    
    top_players_query = (
        db.query(
            player_stats.c.player_id,
            player_stats.c.total_goal_value,
            player_stats.c.total_goals,
            player_stats.c.total_matches
        )
        .order_by(player_stats.c.total_goal_value.desc())
        .limit(limit)
    )
    
    top_players_results = top_players_query.all()
    
    if not top_players_results:
        return []
    
    player_ids = [row.player_id for row in top_players_results]
    players = db.query(Player).filter(Player.id.in_(player_ids)).all()
    players_dict = {player.id: player for player in players}
    
    season_filter_teams = _build_season_filter(ref_season, league_id)
    
    season_query = (
        db.query(PlayerStats.player_id, PlayerStats.team_id)
        .join(Season, PlayerStats.season_id == Season.id)
        .filter(season_filter_teams)
        .filter(PlayerStats.player_id.in_(player_ids))
    )
    
    if league_id is not None:
        season_query = season_query.filter(Season.competition_id == league_id)
    
    player_team_pairs = season_query.distinct().all()
    
    player_teams = {}
    for player_id, team_id in player_team_pairs:
        if player_id not in player_teams:
            player_teams[player_id] = []
        player_teams[player_id].append(team_id)
    
    team_ids = list(set([team_id for teams in player_teams.values() for team_id in teams]))
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    teams_dict = {team.id: team for team in teams}
    
    def build_by_season_player(row) -> BySeasonPlayer:
        player = players_dict[row.player_id]
        
        team_ids_for_player = player_teams.get(row.player_id, [])
        club_names = [teams_dict[tid].name for tid in team_ids_for_player if tid in teams_dict]
        clubs_display = ', '.join(sorted(club_names)) if club_names else '-'
        
        goal_value_avg = calculate_goal_value_avg(row.total_goal_value, row.total_goals)
        
        return BySeasonPlayer(
            player_id=row.player_id,
            player_name=player.name,
            clubs=clubs_display,
            total_goal_value=round(row.total_goal_value, 2) if row.total_goal_value else 0.0,
            goal_value_avg=round(goal_value_avg, 2) if goal_value_avg else 0.0,
            total_goals=int(row.total_goals) if row.total_goals else 0,
            total_matches=int(row.total_matches) if row.total_matches else 0
        )
    
    return [build_by_season_player(row) for row in top_players_results]
