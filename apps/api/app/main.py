"""Main FastAPI application entry point."""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import leagues, clubs, players

app = FastAPI(
    title="Goal Impact API",
    description="Soccer data API",
    version="1.0.0",
)

api_v1 = APIRouter(prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
api_v1.include_router(clubs.router, prefix="/clubs", tags=["clubs"])
api_v1.include_router(players.router, prefix="/players", tags=["players"])

app.include_router(api_v1)

@app.get("/")
async def root():
    return {"message": "Goal Impact API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
