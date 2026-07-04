from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_admin
)

from app.services.kill_service import (
    kill_workspace_agents,
    resume_workspace_agents
)

from app.utils.audit_handler import AuditLogRoute

router = APIRouter(route_class=AuditLogRoute)


# ============================================
# KILL ALL AGENTS
# ============================================

@router.post("/agents/kill")
async def kill_agents(

    workspace_id: str = Header(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    require_admin(
        membership
    )

    return kill_workspace_agents(
        db=db,
        workspace_id=workspace_id,
        current_user=current_user
    )


# ============================================
# RESUME ALL AGENTS
# ============================================

@router.post("/agents/resume")
async def resume_agents(

    workspace_id: str = Header(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    require_admin(
        membership
    )

    return resume_workspace_agents(
        db=db,
        workspace_id=workspace_id,
        current_user=current_user
    )