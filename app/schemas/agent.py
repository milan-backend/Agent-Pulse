from pydantic import BaseModel
from typing import Optional


class AgentCreateRequest(BaseModel):
    name: str


class AgentResponse(BaseModel):
    id: str
    name: str
    api_key: str


class AgentUpdateRequest(BaseModel):

    max_steps: Optional[int] = None

    max_retries: Optional[int] = None

    max_cost: Optional[float] = None

    max_repeated_tasks: Optional[int] = None