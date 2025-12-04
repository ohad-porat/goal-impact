"""Common schemas shared across multiple endpoints."""

from pydantic import BaseModel


class NationInfo(BaseModel):
    """Basic nation information."""

    id: int | None = None
    name: str | None = None
    country_code: str | None = None
