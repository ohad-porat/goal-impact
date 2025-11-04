"""Home router for FastAPI application."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.home import get_recent_impact_goals
from app.schemas.home import RecentImpactGoalsResponse

router = APIRouter()

@router.get("/recent-goals", response_model=RecentImpactGoalsResponse)
async def get_recent_impact_goals_route(
    league_id: Optional[int] = Query(default=None, description="Filter by league/competition ID"),
    db: Session = Depends(get_db)
):
    """Get top 5 goals by goal value from the past week, optionally filtered by league."""
    try:
        goals = get_recent_impact_goals(db, days=7, limit=5, league_id=league_id)
        
        return RecentImpactGoalsResponse(
            goals=goals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent goals: {str(e)}")

