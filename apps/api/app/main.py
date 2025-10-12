from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import leagues

app = FastAPI(
    title="Goal Impact API",
    description="Soccer data API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leagues.router, prefix="/api/leagues", tags=["leagues"])

@app.get("/")
async def root():
    return {"message": "Goal Impact API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
