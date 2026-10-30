from typing import Optional, List
from pydantic import BaseModel, Field

class ShortenRequest(BaseModel):
    url: str = Field(..., description="The target long URL to shorten")
    custom_alias: Optional[str] = Field(None, description="Optional custom key (3-30 alphanumeric characters)")

class ShortenResponse(BaseModel):
    short_url: str
    short_key: str
    original_url: str
    created_at: float

class ClickEventSchema(BaseModel):
    clicked_at: float
    referrer: Optional[str] = ""
    user_agent: Optional[str] = ""

class URLStatsResponse(BaseModel):
    short_key: str
    original_url: str
    created_at: float
    total_clicks: int
    recent_events: List[ClickEventSchema]

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    cached_keys_count: int
