"""Leaders router for FastAPI application."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.leaders import get_career_totals
from app.schemas.leaders import CareerTotalsResponse

router = APIRouter()

@router.get("/career-totals", response_model=CareerTotalsResponse)
async def get_career_totals_leaders(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get top players by career goal value totals."""
    try:
        top_goal_value = get_career_totals(db, limit=limit)
        
        return CareerTotalsResponse(
            top_goal_value=top_goal_value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching career totals: {str(e)}")

