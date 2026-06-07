from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class UserAPIKeyCreate(BaseModel):
    provider: str = Field(
        ..., 
        description="The name of the AI provider, e.g., 'gemini', 'openai'"
    )
    api_key: str = Field(
        ..., 
        description="The plain text raw API key token from the provider console"
    )
    model_version: Optional[str] = Field(
        None, 
        description="The specific version string selected from the dropdown, e.g., 'gpt-4o', 'gemini-2.5-pro'"
    )


class UserAPIKeyResponse(BaseModel):
    id: UUID
    provider: str
    message: str
    model_version: Optional[str] = None
    workspace_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    is_default: bool

    class Config:
        from_attributes = True