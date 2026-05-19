from datetime import datetime

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

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_operator
)

router = APIRouter()


# =========================
# KILL AGENT RUNTIME
# =========================

@router.post("/kill/{agent_id}")
def kill_agent(

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

    # UPDATE AGENT STATE

    agent.is_killed = True

    agent.is_active = False

    # OPTIONAL TRACKING

    agent.killed_at = (
        datetime.utcnow()
    )

    agent.killed_by = (
        current_user.email
    )

    db.commit()

    return {

        "success": True,

        "message":
            "Agent killed successfully",

        "agent_id":
            agent.id,

        "workspace_id":
            workspace_id,

        "controlled_by":
            current_user.email,

        "status":
            "killed"
    }


# =========================
# PAUSE AGENT RUNTIME
# =========================

@router.post("/pause/{agent_id}")
def pause_agent(

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

    # UPDATE STATE

    agent.is_active = False

    # OPTIONAL TRACKING

    agent.paused_at = (
        datetime.utcnow()
    )

    agent.pause_reason = (
        "Paused by operator"
    )

    db.commit()

    return {

        "success": True,

        "message":
            "Agent paused successfully",

        "agent_id":
            agent.id,

        "workspace_id":
            workspace_id,

        "controlled_by":
            current_user.email,

        "status":
            "paused"
    }


# =========================
# RESUME AGENT RUNTIME
# =========================

@router.post("/resume/{agent_id}")
def resume_agent(

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

    # UPDATE STATE

    agent.is_active = True

    agent.is_killed = False

    # OPTIONAL TRACKING

    agent.resumed_at = (
        datetime.utcnow()
    )

    agent.resumed_by = (
        current_user.email
    )

    db.commit()

    return {

        "success": True,

        "message":
            "Agent resumed successfully",

        "agent_id":
            agent.id,

        "workspace_id":
            workspace_id,

        "controlled_by":
            current_user.email,

        "status":
            "active"
    }