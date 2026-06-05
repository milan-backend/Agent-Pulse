from pydantic import BaseModel, Field

class UserAPIKeyCreate(BaseModel):
    provider: str = Field(..., description="The name of the AI provider, e.g., 'gemini'")
    api_key: str = Field(..., description="The plain text raw API key token from the provider console")

class UserAPIKeyResponse(BaseModel):
    provider: str
    message: str

    class Config:
        from_attributes = True