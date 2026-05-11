import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from jose import jwt
from passlib.hash import bcrypt

from datetime import datetime, timedelta

from dotenv import load_dotenv

from app.db.session import get_db

from app.models.user import User
from app.models.agent import Agent

from app.schemas.auth import SignupRequest
import secrets
from passlib.hash import bcrypt
from app.core.security import generate_api_key,hash_api_key


# LOAD ENV
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


router = APIRouter()


# SIGNUP
@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    # check existing user
    existing = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing:
        return {
            "error": "Email already exists"
        }

    # create user
    user = User(
        name=request.name,
        email=request.email,
        password_hash=bcrypt.hash(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    
    # generate real api key
    raw_api_key , key_id = generate_api_key()

# hash api key before saving
    hashed_api_key = hash_api_key(raw_api_key)

    agent = Agent(
      name=f"{request.name}-agent",
      api_key_hash=hashed_api_key,
      key_id=key_id,
      user_id=user.id
)

    db.add(agent)
    db.commit()

    return {
       "message": "Signup successful",
       "user_id": str(user.id),
       "api_key": raw_api_key
}


# LOGIN
@router.post("/login")
def login(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        return {
            "error": "Invalid credentials"
        }

    # verify password
    valid = bcrypt.verify(
        request.password,
        user.password_hash
    )

    if not valid:
        return {
            "error": "Invalid credentials"
        }

    # create jwt payload
    payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    # generate token
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


# TEST AUTH
@router.get("/me")
def me():
    return {
        "message": "Auth working"
    }