from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.nations import (
    get_competitions_for_nation,
    get_top_clubs_for_nation,
    get_top_players_for_nation,
)
from app.core.database import get_db
from app.models.nations import Nation
from app.models.players import Player
from app.schemas.nations import (
    NationsListResponse,
    NationSummary,
    NationDetailsResponse,
    NationInfo,
)

router = APIRouter()

@router.get("/", response_model=NationsListResponse)
async def get_nations(db: Session = Depends(get_db)):
    """Get all nations with their details including player count"""
    nations_query = db.query(
        Nation.id,
        Nation.name,
        Nation.country_code,
        Nation.governing_body,
        func.count(Player.id).label('player_count')
    ).outerjoin(Player, Nation.id == Player.nation_id).group_by(
        Nation.id,
        Nation.name,
        Nation.country_code,
        Nation.governing_body
    ).order_by(Nation.name).all()
    
    nations_data = [
        NationSummary(
            id=nation.id,
            name=nation.name,
            country_code=nation.country_code,
            governing_body=nation.governing_body or "N/A",
            player_count=nation.player_count
        )
        for nation in nations_query
    ]
    
    return NationsListResponse(nations=nations_data)


@router.get("/{nation_id}", response_model=NationDetailsResponse)
async def get_nation_details(
    nation_id: int,
    db: Session = Depends(get_db),
):
    """Get nation details: competitions, top 10 clubs, top 20 players."""

    nation = db.query(Nation).filter(Nation.id == nation_id).first()
    if not nation:
        raise HTTPException(status_code=404, detail="Nation not found")

    competitions_data = get_competitions_for_nation(db, nation_id)
    clubs_data = get_top_clubs_for_nation(db, nation_id, limit=10)
    players_data = get_top_players_for_nation(db, nation_id, limit=20)

    from app.schemas.nations import CompetitionSummary, ClubSummary, PlayerSummary

    return NationDetailsResponse(
        nation=NationInfo(
            id=nation.id,
            name=nation.name,
            country_code=nation.country_code,
            governing_body=nation.governing_body or "N/A",
        ),
        competitions=[CompetitionSummary(**comp) for comp in competitions_data],
        clubs=[ClubSummary(**club) for club in clubs_data],
        players=[PlayerSummary(**player) for player in players_data],
    )
