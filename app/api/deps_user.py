from fastapi import (
    Depends,Request
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.services.user_auth_service import (
    authenticate_user
)


security = HTTPBearer()


def get_current_user(
        request: Request,

    credentials:
        HTTPAuthorizationCredentials
        = Depends(security),

    db: Session = Depends(get_db)

):

    token = credentials.credentials

    return authenticate_user(
        db=db,
        token=token
    )

    # 🟢 Step 2: Bind the user object straight to the request state layer!
    request.state.user = user

    return user