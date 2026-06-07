from typing import Optional
from pydantic import BaseModel
from app.db.enums import AgentStatus


class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    
    # Optional fields for setting up an API provider immediately during agent creation
    api_provider: Optional[str] = None     # 'openai', 'gemini'
    agent_api_key: Optional[str] = None    # Raw API Key token
    model_version: Optional[str] = None    # E.g., 'gpt-4o', 'gemini-1.5-pro'


# Keep this strictly focused on policy limits, exactly how it should be!
class AgentPolicyUpdateRequest(BaseModel):
    max_steps: Optional[int] = None
    max_retries: Optional[int] = None
    max_cost: Optional[float] = None
    max_repeated_tasks: Optional[int] = None


# Add a dedicated agent update class to handle settings and task connection overrides cleanly
class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_provider: Optional[str] = None     # 'openai', 'gemini'
    agent_api_key: Optional[str] = None    # Raw API Key token
    model_version: Optional[str] = None    # E.g., 'gpt-4o', 'gemini-1.5-pro'


class AgentResponse(BaseModel):
    id: str
    name: str
    status: AgentStatus
    workspace_id: str
    created_by: str
    total_cost: float
    mission_count: int
    created_at: str


class AgentCreateResponse(BaseModel):
    id: str
    name: str
    api_key: str