from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import authenticate_agent


api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)


def get_current_agent(
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
):
    return authenticate_agent(
        db=db,
        api_key=api_key
    )