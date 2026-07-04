from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.workspace import Workspace

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_operator
)

from app.services.feature_access import (
    require_feature
)

from app.services.mission_control_service import (
    kill_agent_runtime,
    pause_agent_runtime,
    resume_agent_runtime
)

from app.utils.audit_handler import AuditLogRoute

router = APIRouter(route_class=AuditLogRoute)


# ============================================
# VALIDATE RUNTIME FEATURE
# ============================================

def validate_runtime_feature(
    db,
    workspace_id,
    feature_name
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if not workspace:

        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    require_feature(
        workspace,
        feature_name
    )


# ============================================
# KILL AGENT
# ============================================

@router.post("/kill/{agent_id}")
def kill_agent(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    require_operator(
        membership
    )

    validate_runtime_feature(
        db,
        workspace_id,
        "single_agent_kill"
    )

    return kill_agent_runtime(
        db=db,
        workspace_id=workspace_id,
        agent_id=agent_id,
        current_user=current_user
    )


# ============================================
# PAUSE AGENT
# ============================================

@router.post("/pause/{agent_id}")
def pause_agent(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    require_operator(
        membership
    )

    validate_runtime_feature(
        db,
        workspace_id,
        "single_agent_pause"
    )

    return pause_agent_runtime(
        db=db,
        workspace_id=workspace_id,
        agent_id=agent_id,
        current_user=current_user
    )


# ============================================
# RESUME AGENT
# ============================================

@router.post("/resume/{agent_id}")
def resume_agent(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    require_operator(
        membership
    )

    validate_runtime_feature(
        db,
        workspace_id,
        "single_agent_resume"
    )

    return resume_agent_runtime(
        db=db,
        workspace_id=workspace_id,
        agent_id=agent_id,
        current_user=current_user
    )