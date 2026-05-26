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