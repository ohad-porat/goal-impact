"""Search router for FastAPI application."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import SearchResponse
from app.services.search import search_all

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"), db: Session = Depends(get_db)
):
    """Search across players, clubs, competitions, and nations."""
    results = search_all(db, q, limit_per_type=5)

    return SearchResponse(results=results)
