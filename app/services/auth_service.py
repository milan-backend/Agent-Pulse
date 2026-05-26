from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.agent import Agent

from app.core.security import (
    verify_api_key
)


def authenticate_agent(
    db: Session,
    api_key: str
):

    if not api_key:

        raise HTTPException(
            status_code=401,
            detail="API Key missing"
        )

    # EXTRACT KEY ID
    try:

        key_id = api_key.split(".")[0]

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid API Key format"
        )

    # FIND AGENT
    agent = (
        db.query(Agent)
        .filter(
            Agent.key_id == key_id
        )
        .first()
    )

    if not agent:

        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    # AGENT STATUS CHECKS
    if agent.status == "killed":

        raise HTTPException(
            status_code=403,
            detail="Agent has been killed"
        )

    if not agent.is_active:

        raise HTTPException(
            status_code=403,
            detail="Agent inactive"
        )

    # VERIFY HASH
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