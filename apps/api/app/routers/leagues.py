from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.competitions import Competition
from app.models.nations import Nation
from app.models.seasons import Season

router = APIRouter()

@router.get("/")
async def get_leagues(db: Session = Depends(get_db)):
    """Get all available leagues with their details"""
    competitions = db.query(Competition).join(Nation).all()
    
    leagues_data = []
    for competition in competitions:
        seasons = db.query(Season).filter(Season.competition_id == competition.id).all()
        
        if seasons:
            sorted_seasons = sorted(seasons, key=lambda s: s.start_year)
            first_season = sorted_seasons[0]
            last_season = sorted_seasons[-1]
            
            if first_season.start_year == first_season.end_year and last_season.start_year == last_season.end_year:
                available_seasons = f"{first_season.start_year} - {last_season.start_year}"
            else:
                available_seasons = f"{first_season.start_year}/{first_season.end_year} - {last_season.start_year}/{last_season.end_year}"
        else:
            available_seasons = "No seasons available"
        
        league_info = {
            "id": competition.id,
            "name": competition.name,
            "country": competition.nation.name if competition.nation else "Unknown",
            "gender": competition.gender,
            "tier": competition.tier,
            "available_seasons": available_seasons
        }
        leagues_data.append(league_info)
    
    return {"leagues": leagues_data}
