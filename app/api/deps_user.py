import os

from dotenv import load_dotenv

from jose import (
    jwt,
    JWTError
)

from fastapi import (
    Depends,
    HTTPException
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User


# LOAD ENV

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)

ALGORITHM = os.getenv(
    "ALGORITHM"
)

security = HTTPBearer()


# =========================
# GET CURRENT USER
# =========================

def get_current_user(

    credentials:
        HTTPAuthorizationCredentials
        = Depends(security),

    db: Session = Depends(get_db)
):

    # GET TOKEN

    token = credentials.credentials

    try:

        # DECODE JWT

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # GET USER ID

        user_id = payload.get(
            "sub"
        )

        if not user_id:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # FIND USER

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user