from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
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
