"""FastAPI configuration settings."""

from typing import List

class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Goal Impact API"
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
