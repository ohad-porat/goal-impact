from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.database import get_db
from app.models.nations import Nation
from app.models.teams import Team
from app.models.team_stats import TeamStats
from app.models.competitions import Competition
from app.models.seasons import Season

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
