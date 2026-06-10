from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class UserAPIKeyCreate(BaseModel):
    provider: str = Field(
        ..., 
        description="The engine type of the AI provider, e.g., 'gemini', 'openai'"
    )
    api_key: str = Field(
        ..., 
        description="The plain text raw API key token from the provider console"
    )
    model_version: Optional[str] = Field(
        None, 
        description="The specific version string selected from the dropdown, e.g., 'gpt-4o', 'gemini-2.5-flash-lite'"
    )
    
    # =========================================================================
    # NEW ARCHITECTURE UPGRADE ADDITIONS
    # =========================================================================
    provider_name: Optional[str] = Field(
        "Workspace Provider",
        description="Custom label/name to distinguish multiple keys from the same provider (e.g., 'OpenAI Production')"
    )
    assigned_agents: Optional[List[str]] = Field(
        default=[],
        description="List of specific Agent UUID strings allowed to route through this provider key configuration"
    )
    is_global_default: Optional[bool] = Field(
        False,
        description="If True, acts as the global fallback provider for all unassigned agents in the workspace"
    )


class UserAPIKeyResponse(BaseModel):
    id: UUID
    provider: str
    message: str
    model_version: Optional[str] = None
    workspace_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    is_default: bool
    
    # =========================================================================
    # NEW ARCHITECTURE UPGRADE ADDITIONS
    # =========================================================================
    provider_name: Optional[str] = None
    assigned_agents: List[str] = []
    is_global_default: bool

    class Config:
        from_attributes = True