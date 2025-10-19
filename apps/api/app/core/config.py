"""FastAPI configuration settings."""

import os
import json
from typing import List
from dotenv import load_dotenv

load_dotenv('.env.local')

class Settings:
    ALLOWED_HOSTS: List[str] = json.loads(os.getenv("ALLOWED_HOSTS"))

settings = Settings()
