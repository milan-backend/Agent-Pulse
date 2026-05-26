from typing import Optional

from pydantic import BaseModel

from app.db.enums import AgentStatus


class AgentCreateRequest(BaseModel):

    name: str

    description: Optional[str] = None


class AgentPolicyUpdateRequest(BaseModel):

    max_steps: Optional[int] = None

    max_retries: Optional[int] = None

    max_cost: Optional[float] = None

    max_repeated_tasks: Optional[int] = None


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