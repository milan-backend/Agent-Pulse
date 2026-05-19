from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.agent import Agent
from app.core.security import verify_api_key


api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)


def get_current_agent(
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key missing"
        )

    # 🔥 Extract key_id
    try:
        key_id = api_key.split(".")[0]

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key format"
        )

    # ⚡ Find ONE agent only
    agent = db.query(Agent).filter(
        Agent.key_id == key_id,
    ).first()

    if not agent:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    
    if agent.is_killed:
        raise HTTPException(
            status_code=403,
            detail= "Agent has been killed"
        )
    
    if not agent.is_active:
        raise HTTPException(
            status_code=403,
            detail= "Agent inactive"
        )

    # 🔐 Verify secret
    valid = verify_api_key(
        api_key,
        agent.api_key_hash
    )

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return agent