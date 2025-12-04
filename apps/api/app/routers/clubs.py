from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.clubs import (
    ClubDetailsResponse,
    ClubsByNationResponse,
    TeamSeasonGoalLogResponse,
    TeamSeasonSquadResponse,
)
from app.services.clubs import (
    get_club_with_seasons,
    get_clubs_by_nation,
    get_team_season_goal_log,
    get_team_season_squad_stats,
)

router = APIRouter()


@router.get("/", response_model=ClubsByNationResponse)
async def get_clubs_by_nation_route(db: Session = Depends(get_db)):
    """Get top 5 clubs per nation based on average finishing position in tier 1 leagues"""
    result = get_clubs_by_nation(db, limit_per_nation=5)
    return ClubsByNationResponse(nations=result)


@router.get("/{club_id}", response_model=ClubDetailsResponse)
async def get_club_details(club_id: int, db: Session = Depends(get_db)):
    """Get detailed club information with season statistics"""
    club_info, seasons_data = get_club_with_seasons(db, club_id)

    if not club_info:
        raise HTTPException(status_code=404, detail="Club not found")

    return ClubDetailsResponse(club=club_info, seasons=seasons_data)


@router.get("/{team_id}/seasons/{season_id}", response_model=TeamSeasonSquadResponse)
async def get_team_season_squad(team_id: int, season_id: int, db: Session = Depends(get_db)):
    """Get team squad with player statistics for a specific season"""
    club_info, season_display, competition_display, players_data = get_team_season_squad_stats(
        db, team_id, season_id
    )

    if not club_info or not season_display:
        if not club_info:
            raise HTTPException(status_code=404, detail="Team not found")
        else:
            raise HTTPException(status_code=404, detail="Season not found")

    return TeamSeasonSquadResponse(
        team=club_info, season=season_display, competition=competition_display, players=players_data
    )


@router.get("/{team_id}/seasons/{season_id}/goals", response_model=TeamSeasonGoalLogResponse)
async def get_team_season_goal_log_route(
    team_id: int, season_id: int, db: Session = Depends(get_db)
):
    """Get goal log for a team in a specific season"""
    club_info, season_display, competition_display, goals_data = get_team_season_goal_log(
        db, team_id, season_id
    )

    if not club_info or not season_display:
        if not club_info:
            raise HTTPException(status_code=404, detail="Team not found")
        else:
            raise HTTPException(status_code=404, detail="Season not found")

    return TeamSeasonGoalLogResponse(
        team=club_info, season=season_display, competition=competition_display, goals=goals_data
    )
