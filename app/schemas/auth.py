from pydantic import (
    BaseModel,
    EmailStr
)


class SignupRequest(BaseModel):

    name: str | None = None

    email: EmailStr

    password: str


class LoginRequest(BaseModel):

    email: EmailStr

    password: str

class ForgetPasswordRequest(BaseModel):

    email : EmailStr

class ResetPasswordRequest(BaseModel):

    token: str

    new_password: str


# ============================================
# DEACTIVATE ACCOUNT
# ============================================

class DeactivateAccountRequest(
    BaseModel
):

    password: str


class SSOLoginRequest(BaseModel):
    email: EmailStr
    name: str
    provider: str      # e.g., "google" or "github"
    provider_id: str   # The unique ID string sent by Google/GitHub API