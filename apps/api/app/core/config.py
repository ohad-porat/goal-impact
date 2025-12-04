"""FastAPI configuration settings."""

import json
import os

from dotenv import load_dotenv

load_dotenv(".env.local")


class Settings:
    ALLOWED_HOSTS: list[str] = json.loads(os.getenv("ALLOWED_HOSTS"))


settings = Settings()
