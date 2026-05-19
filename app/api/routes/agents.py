import uuid
import secrets

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.agent import Agent
from app.models.user import User

from app.schemas.agent import (
    AgentCreateRequest,
    AgentResponse,
    AgentUpdateRequest
)

from app.core.security import (
    hash_api_key,
    generate_api_key
)

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_admin,
    require_operator
)

router = APIRouter()


# =========================
# CREATE AGENT
# =========================

@router.post(
    "/",
    response_model=AgentResponse
)
def create_agent(

    request: AgentCreateRequest,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # REQUIRE OPERATOR

    require_operator(membership)

    # GENERATE KEY PARTS

    key_id = str(uuid.uuid4())

    secret = secrets.token_hex(16)

    # FULL API KEY

    api_key, key_id = (
        generate_api_key()
    )

    # STORE ONLY HASH

    hashed_key = hash_api_key(
        api_key
    )

    # CREATE AGENT

    agent = Agent(

        id=str(uuid.uuid4()),

        name=request.name,

        api_key_hash=hashed_key,

        key_id=key_id,

        is_active=True,

        user_id=current_user.id,

        workspace_id=workspace_id
    )

    db.add(agent)

    db.commit()

    db.refresh(agent)

    return AgentResponse(

        id=agent.id,

        name=agent.name,

        api_key=api_key
    )


# =========================
# REGENERATE API KEY
# =========================

@router.post(
    "/regenerate-key/{agent_id}"
)
def regenerate_api_key(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # REQUIRE ADMIN

    require_admin(membership)

    # FIND AGENT

    agent = db.query(Agent).filter(

        Agent.id == agent_id,

        Agent.workspace_id ==
        workspace_id

    ).first()

    if not agent:

        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    # GENERATE NEW KEY

    raw_api_key, key_id = (
        generate_api_key()
    )

    # SAVE HASHED KEY

    agent.api_key_hash = (
        hash_api_key(raw_api_key)
    )

    agent.key_id = key_id

    db.commit()

    return {

        "message":
            "API key regenerated",

        "api_key":
            raw_api_key
    }


# =========================
# UPDATE AGENT
# =========================

@router.put("/{agent_id}")
def update_agent(

    agent_id: str,

    request: AgentUpdateRequest,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # REQUIRE OPERATOR

    require_operator(membership)

    # FIND AGENT

    agent = db.query(Agent).filter(

        Agent.id == agent_id,

        Agent.workspace_id ==
        workspace_id

    ).first()

    if not agent:

        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    # UPDATE SETTINGS

    if request.max_steps is not None:

        agent.max_steps = (
            request.max_steps
        )

    if request.max_retries is not None:

        agent.max_retries = (
            request.max_retries
        )

    if request.max_cost is not None:

        agent.max_cost = (
            request.max_cost
        )

    if request.max_repeated_tasks is not None:

        agent.max_repeated_tasks = (
            request.max_repeated_tasks
        )

    db.commit()

    db.refresh(agent)

    return {

        "success": True,

        "message":
            "Agent updated successfully",

        "agent": {

            "id":
                str(agent.id),

            "max_steps":
                agent.max_steps,

            "max_retries":
                agent.max_retries,

            "max_cost":
                agent.max_cost,

            "max_repeated_tasks":
                agent.max_repeated_tasks
        }
    }