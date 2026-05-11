from pydantic import BaseModel


class AgentCreateRequest(BaseModel):
    name: str


class AgentResponse(BaseModel):
    id: str
    name: str
    api_key: str