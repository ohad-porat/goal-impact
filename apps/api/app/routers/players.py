"""Players router for FastAPI application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.players import get_player_seasons_stats
from app.schemas.players import PlayerDetailsResponse

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
