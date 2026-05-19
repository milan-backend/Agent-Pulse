from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status
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
    require_admin
)

router = APIRouter()


# =========================
# KILL ALL AGENTS
# =========================

@router.post("/agents/kill")
async def kill_agents(

    workspace_id: str = Header(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
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

    # KILL AGENTS

    updated_count = (
        db.query(Agent)
        .filter(
            Agent.workspace_id
            == workspace_id
        )
        .update(
            {"is_killed": True},
            synchronize_session=False
        )
    )

    db.commit()

    return {

        "message":
            "Emergency stop activated",

        "killed_agents":
            updated_count,

        "workspace_id":
            workspace_id,

        "user":
            current_user.email
    }


# =========================
# RESUME ALL AGENTS
# =========================

@router.post("/agents/resume")
async def resume_agents(

    workspace_id: str = Header(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
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

    # RESUME AGENTS

    updated_count = (
        db.query(Agent)
        .filter(
            Agent.workspace_id
            == workspace_id
        )
        .update(
            {"is_killed": False},
            synchronize_session=False
        )
    )

    db.commit()

    return {

        "message":
            "Agents resumed",

        "resumed_agents":
            updated_count,

        "workspace_id":
            workspace_id,

        "user":
            current_user.email
    }