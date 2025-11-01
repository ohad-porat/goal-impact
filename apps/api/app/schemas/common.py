"""Common schemas shared across multiple endpoints."""

from typing import Optional
from pydantic import BaseModel


class NationInfo(BaseModel):
    """Basic nation information."""
    
    id: Optional[int]
    name: Optional[str]
    country_code: Optional[str]

