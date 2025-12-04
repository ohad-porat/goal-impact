"""Main FastAPI application entry point."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.routers import clubs, home, leaders, leagues, nations, players, search

app = FastAPI(
    title="Goal Impact API",
    description="Soccer data API",
    version="1.0.0",
)

api_v1 = APIRouter(prefix="/api/v1")

app.add_middleware(GZipMiddleware, minimum_size=1000)

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
api_v1.include_router(nations.router, prefix="/nations", tags=["nations"])
api_v1.include_router(leaders.router, prefix="/leaders", tags=["leaders"])
api_v1.include_router(home.router, prefix="/home", tags=["home"])
api_v1.include_router(search.router, prefix="/search", tags=["search"])

app.include_router(api_v1)


@app.get("/")
async def root():
    return {"message": "Goal Impact API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
