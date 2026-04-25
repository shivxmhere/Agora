from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AgentCard(BaseModel):
    id: str
    name: str
    tagline: str
    category: str
    rating: float
    total_runs: int
    status: str
    creator_name: str
    creator_score: float
    tags: List[str]

class AgentDetail(AgentCard):
    description: str
    long_description: str
    capabilities: List[str]
    avg_run_time: float
    success_rate: float
    pricing_model: str
    price_per_run: int
    input_placeholder: str

class AgentCreate(BaseModel):
    name: str
    tagline: str
    description: str
    long_description: Optional[str] = ""
    category: str
    tags: List[str]
    creator_name: str
    capabilities: List[str]
    input_placeholder: str

class RunCreate(BaseModel):
    input: str
    session_id: str

class RunResponse(BaseModel):
    run_id: str
    stream_url: str

class RunStatusResponse(BaseModel):
    status: str
    output: Optional[str] = None
    run_time: Optional[float] = None

class RatingCreate(BaseModel):
    stars: int = Field(ge=1, le=5)
    review: Optional[str] = ""
    session_id: str

class ActivityLog(BaseModel):
    agent_name: str
    action: str
    location: str
    time: str  # e.g., "now", "2s ago"

class AnalyticsResponse(BaseModel):
    total_runs: int
    total_earnings: float
    avg_rating: float
    top_agent: str
    runs_by_day: Dict[str, int]
    runs_by_agent: Dict[str, int]
