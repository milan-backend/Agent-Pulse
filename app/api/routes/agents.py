import uuid
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreateRequest, AgentResponse
from app.core.security import hash_api_key
from app.core.security import generate_api_key
from app.api.deps_user import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=AgentResponse)
def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db)
):
    # 🔥 generate key parts
    key_id = str(uuid.uuid4())
    secret = secrets.token_hex(16)

    # full api key (what user sees)
    api_key, key_id = generate_api_key()

    # store only hash
    hashed_key = hash_api_key(api_key)

    agent = Agent(
        id=str(uuid.uuid4()),  # if not auto
        name=request.name,
        api_key_hash=hashed_key,
        key_id=key_id,
        is_active=True
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        api_key=api_key
    )


@router.post("/regenerate-key")
def regenerate_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = db.query(Agent).filter(
        Agent.user_id == current_user.id
    ).first()

    if not agent:
        return {"error": "Agent not found"}

    # generate new key
    raw_api_key, key_id = generate_api_key()

    # save hashed key
    agent.api_key_hash = hash_api_key(raw_api_key)
    agent.key_id = key_id

    db.commit()

    return {
        "message": "API key regenerated",
        "api_key": raw_api_key
    }