from pydantic import BaseModel,EmailStr

class SignupRequest(BaseModel):
    name : str | None = None
    email : EmailStr
    password : str