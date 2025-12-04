from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.competitions import Competition
from app.schemas.leagues import (
    LeagueSeasonsResponse,
    LeaguesListResponse,
    LeagueTableResponse,
)
from app.services.leagues import (
    get_all_leagues_with_season_ranges,
    get_all_unique_seasons,
    get_league_seasons,
    get_league_table_for_season,
)

router = APIRouter()


@router.get("/", response_model=LeaguesListResponse)
async def get_leagues(db: Session = Depends(get_db)):
    """Get all available leagues with their details"""
    leagues_data = get_all_leagues_with_season_ranges(db)
    return LeaguesListResponse(leagues=leagues_data)


@router.get("/seasons", response_model=LeagueSeasonsResponse)
async def get_all_seasons_route(db: Session = Depends(get_db)):
    """Get all unique seasons across all leagues, sorted by start_year descending."""
    seasons_data = get_all_unique_seasons(db)
    return LeagueSeasonsResponse(seasons=seasons_data)


@router.get("/{league_id}/seasons", response_model=LeagueSeasonsResponse)
async def get_league_seasons_route(league_id: int, db: Session = Depends(get_db)):
    """Get all available seasons for a specific league"""
    competition = db.query(Competition).filter(Competition.id == league_id).first()
    if not competition:
        raise HTTPException(status_code=404, detail="League not found")

    seasons_data = get_league_seasons(db, league_id)
    return LeagueSeasonsResponse(seasons=seasons_data)


@router.get("/{league_id}/table/{season_id}", response_model=LeagueTableResponse)
async def get_league_table(league_id: int, season_id: int, db: Session = Depends(get_db)):
    """Get league table for a specific league and season"""
    league_info, season_info, table_data = get_league_table_for_season(db, league_id, season_id)

    if not league_info or not season_info:
        if not league_info:
            raise HTTPException(status_code=404, detail="League not found")
        else:
            raise HTTPException(status_code=404, detail="Season not found for this league")

    return LeagueTableResponse(league=league_info, season=season_info, table=table_data)
