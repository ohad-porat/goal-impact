"""Players router for FastAPI application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.players import get_player_seasons_stats, get_player_career_goal_log
from app.schemas.players import PlayerDetailsResponse
from app.schemas.clubs import PlayerGoalLogResponse

router = APIRouter()

@router.get("/{player_id}", response_model=PlayerDetailsResponse)
async def get_player_details(player_id: int, db: Session = Depends(get_db)):
    """Get detailed player information with statistics across all seasons"""
    player_info, seasons_data = get_player_seasons_stats(db, player_id)
    
    if not player_info:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return PlayerDetailsResponse(
        player=player_info,
        seasons=seasons_data
    )

@router.get("/{player_id}/goals", response_model=PlayerGoalLogResponse)
async def get_player_career_goal_log_route(player_id: int, db: Session = Depends(get_db)):
    """Get goal log for a player across their entire career."""
    player_basic, goals_data = get_player_career_goal_log(db, player_id)
    
    if not player_basic:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return PlayerGoalLogResponse(
        player=player_basic,
        goals=goals_data
    )
