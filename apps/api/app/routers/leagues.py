from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.competitions import Competition
from app.models.nations import Nation
from app.models.seasons import Season
from app.models.team_stats import TeamStats
from app.models.teams import Team
from app.schemas.leagues import (
    LeaguesListResponse,
    LeagueSummary,
    LeagueSeasonsResponse,
    SeasonInfo,
    LeagueTableResponse,
    LeagueInfo,
    LeagueTableEntry,
)

router = APIRouter()

@router.get("/", response_model=LeaguesListResponse)
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
        
        leagues_data.append(
            LeagueSummary(
                id=competition.id,
                name=competition.name,
                country=competition.nation.name if competition.nation else "Unknown",
                gender=competition.gender,
                tier=competition.tier,
                available_seasons=available_seasons
            )
        )
    
    return LeaguesListResponse(leagues=leagues_data)

@router.get("/{league_id}/seasons", response_model=LeagueSeasonsResponse)
async def get_league_seasons(league_id: int, db: Session = Depends(get_db)):
    """Get all available seasons for a specific league"""
    competition = db.query(Competition).filter(Competition.id == league_id).first()
    
    if not competition:
        raise HTTPException(status_code=404, detail="League not found")
    
    seasons = db.query(Season).filter(Season.competition_id == league_id).all()
    
    seasons_data = [
        SeasonInfo(
            id=season.id,
            start_year=season.start_year,
            end_year=season.end_year,
            display_name=f"{season.start_year}/{season.end_year}" if season.start_year != season.end_year else str(season.start_year)
        )
        for season in seasons
    ]
    
    seasons_data.sort(key=lambda x: x.start_year, reverse=True)
    
    return LeagueSeasonsResponse(seasons=seasons_data)

@router.get("/{league_id}/table/{season_id}", response_model=LeagueTableResponse)
async def get_league_table(league_id: int, season_id: int, db: Session = Depends(get_db)):
    """Get league table for a specific league and season"""
    competition = db.query(Competition).filter(Competition.id == league_id).first()
    if not competition:
        raise HTTPException(status_code=404, detail="League not found")
    
    season = db.query(Season).filter(
        Season.id == season_id,
        Season.competition_id == league_id
    ).first()
    if not season:
        raise HTTPException(status_code=404, detail="Season not found for this league")
    
    team_stats = db.query(TeamStats).join(Team).filter(
        TeamStats.season_id == season_id
    ).order_by(TeamStats.ranking).all()
    
    table_data = [
        LeagueTableEntry(
            position=stats.ranking,
            team_id=stats.team.id,
            team_name=stats.team.name,
            matches_played=stats.matches_played,
            wins=stats.wins,
            draws=stats.draws,
            losses=stats.losses,
            goals_for=stats.goals_for,
            goals_against=stats.goals_against,
            goal_difference=stats.goal_difference,
            points=stats.points
        )
        for stats in team_stats
    ]
    
    return LeagueTableResponse(
        league=LeagueInfo(
            id=competition.id,
            name=competition.name,
            country=competition.nation.name if competition.nation else "Unknown"
        ),
        season=SeasonInfo(
            id=season.id,
            start_year=season.start_year,
            end_year=season.end_year,
            display_name=f"{season.start_year}/{season.end_year}" if season.start_year != season.end_year else str(season.start_year)
        ),
        table=table_data
    )
