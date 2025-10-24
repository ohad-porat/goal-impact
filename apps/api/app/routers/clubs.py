from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.database import get_db
from app.models.nations import Nation
from app.models.teams import Team
from app.models.team_stats import TeamStats
from app.models.competitions import Competition
from app.models.seasons import Season
from app.models.players import Player
from app.models.player_stats import PlayerStats

router = APIRouter()

@router.get("/")
async def get_clubs_by_nation(db: Session = Depends(get_db)):
    """Get top 5 clubs per nation based on average finishing position in tier 1 leagues"""
    
    nations_with_competitions = db.query(Nation).join(Competition).distinct().all()
    
    result = []
    
    for nation in nations_with_competitions:
        teams_with_avg_position = db.query(
            Team.id,
            Team.name,
            func.avg(TeamStats.ranking).label('avg_position')
        ).join(TeamStats).join(Season).join(Competition).filter(
            Team.nation_id == nation.id,
            Competition.tier == '1st',
            TeamStats.ranking.isnot(None)
        ).group_by(Team.id, Team.name).order_by(
            'avg_position',
            Team.name
        ).limit(5).all()
        
        clubs = []
        for team in teams_with_avg_position:
            clubs.append({
                "id": team.id,
                "name": team.name,
                "avg_position": round(float(team.avg_position), 1)
            })
        
        if clubs:
            result.append({
                "nation": {
                    "id": nation.id,
                    "name": nation.name,
                    "country_code": nation.country_code
                },
                "clubs": clubs
            })
    
    return {"nations": result}

@router.get("/{club_id}")
async def get_club_details(club_id: int, db: Session = Depends(get_db)):
    """Get detailed club information with season statistics"""
    
    try:
        team = db.query(Team).options(joinedload(Team.nation)).filter(Team.id == club_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Club not found")
        
        team_stats_query = db.query(
            TeamStats,
            Season,
            Competition
        ).select_from(TeamStats).join(Season).join(Competition).filter(
            TeamStats.team_id == club_id
        ).order_by(
            Season.start_year.desc(),
            Competition.name
        ).all()
        
        seasons_data = []
        for team_stat, season, competition in team_stats_query:
            seasons_data.append({
                "season": {
                    "id": season.id,
                    "start_year": season.start_year,
                    "end_year": season.end_year,
                    "year_range": f"{season.start_year}/{season.end_year}" if season.end_year else str(season.start_year)
                },
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "tier": competition.tier
                },
                "stats": {
                    "ranking": team_stat.ranking,
                    "matches_played": team_stat.matches_played,
                    "wins": team_stat.wins,
                    "draws": team_stat.draws,
                    "losses": team_stat.losses,
                    "goals_for": team_stat.goals_for,
                    "goals_against": team_stat.goals_against,
                    "goal_difference": team_stat.goal_difference,
                    "points": team_stat.points,
                    "attendance": team_stat.attendance,
                    "notes": team_stat.notes
                }
            })
        
        return {
            "club": {
                "id": team.id,
                "name": team.name,
                "nation": {
                    "id": team.nation.id if team.nation else None,
                    "name": team.nation.name if team.nation else "Unknown",
                    "country_code": team.nation.country_code if team.nation else None
                }
            },
            "seasons": seasons_data
        }
    except Exception as e:
        print(f"Error in get_club_details: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{team_id}/seasons/{season_id}")
async def get_team_season_squad(team_id: int, season_id: int, db: Session = Depends(get_db)):
    """Get team squad with player statistics for a specific season"""
    
    try:
        team = db.query(Team).options(joinedload(Team.nation)).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        season = db.query(Season).options(joinedload(Season.competition)).filter(Season.id == season_id).first()
        if not season:
            raise HTTPException(status_code=404, detail="Season not found")
        
        player_stats_query = db.query(
            PlayerStats,
            Player
        ).select_from(PlayerStats).join(Player).filter(
            PlayerStats.team_id == team_id,
            PlayerStats.season_id == season_id
        ).order_by(PlayerStats.goal_value.desc()).all()
        
        players_data = []
        for stats, player in player_stats_query:
            players_data.append({
                "player": {
                    "id": player.id,
                    "name": player.name
                },
                "stats": {
                    "matches_played": stats.matches_played,
                    "matches_started": stats.matches_started,
                    "total_minutes": stats.total_minutes,
                    "minutes_divided_90": round(stats.minutes_divided_90, 2) if stats.minutes_divided_90 else None,
                    "goals_scored": stats.goals_scored,
                    "assists": stats.assists,
                    "total_goal_assists": stats.total_goal_assists,
                    "non_pk_goals": stats.non_pk_goals,
                    "pk_made": stats.pk_made,
                    "pk_attempted": stats.pk_attempted,
                    "yellow_cards": stats.yellow_cards,
                    "red_cards": stats.red_cards,
                    "goal_value": round(stats.goal_value, 2) if stats.goal_value is not None else None,
                    "gv_avg": round(stats.gv_avg, 2) if stats.gv_avg is not None else None,
                    "goal_per_90": round(stats.goal_per_90, 2) if stats.goal_per_90 is not None else None,
                    "assists_per_90": round(stats.assists_per_90, 2) if stats.assists_per_90 is not None else None,
                    "total_goals_assists_per_90": round(stats.total_goals_assists_per_90, 2) if stats.total_goals_assists_per_90 is not None else None,
                    "non_pk_goals_per_90": round(stats.non_pk_goals_per_90, 2) if stats.non_pk_goals_per_90 is not None else None,
                    "non_pk_goal_and_assists_per_90": round(stats.non_pk_goal_and_assists_per_90, 2) if stats.non_pk_goal_and_assists_per_90 is not None else None
                }
            })
        
        return {
            "team": {
                "id": team.id,
                "name": team.name,
                "nation": {
                    "id": team.nation.id if team.nation else None,
                    "name": team.nation.name if team.nation else "Unknown",
                    "country_code": team.nation.country_code if team.nation else None
                }
            },
            "season": {
                "id": season.id,
                "start_year": season.start_year,
                "end_year": season.end_year,
                "display_name": f"{season.start_year}/{season.end_year}" if season.start_year != season.end_year else str(season.start_year)
            },
            "competition": {
                "id": season.competition.id if season.competition else None,
                "name": season.competition.name if season.competition else "Unknown"
            },
            "players": players_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_team_season_squad: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
