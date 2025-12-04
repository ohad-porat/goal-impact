from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.nations import Nation
from app.schemas.nations import (
    CompetitionSummary,
    NationDetails,
    NationDetailsResponse,
    NationsListResponse,
    PlayerSummary,
)
from app.services.clubs import get_top_clubs_for_nation_core
from app.services.nations import (
    get_all_nations_with_player_count,
    get_competitions_for_nation,
    get_top_players_for_nation,
)

router = APIRouter()


@router.get("/", response_model=NationsListResponse)
async def get_nations(db: Session = Depends(get_db)):
    """Get all nations with their details including player count"""
    nations_data = get_all_nations_with_player_count(db)
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
    clubs_data = get_top_clubs_for_nation_core(db, nation_id, limit=10)
    players_data = get_top_players_for_nation(db, nation_id, limit=20)

    return NationDetailsResponse(
        nation=NationDetails(
            id=nation.id,
            name=nation.name,
            country_code=nation.country_code,
            governing_body=nation.governing_body or "N/A",
        ),
        competitions=[CompetitionSummary(**competition) for competition in competitions_data],
        clubs=clubs_data,
        players=[PlayerSummary(**player) for player in players_data],
    )
