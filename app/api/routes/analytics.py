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

from app.services.analytics_service import (
    get_cost_analytics_data,
    get_blocked_missions_data,
    get_agent_analytics_data,
    get_analytics_overview_data
)

from app.utils.audit_handler import AuditLogRoute

router = APIRouter(route_class=AuditLogRoute)


# =========================
# COST ANALYTICS
# =========================

@router.get("/costs")
def get_cost_analytics(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    return get_cost_analytics_data(
        db=db,
        workspace_id=workspace_id
    )


# =========================
# BLOCKED MISSIONS
# =========================

@router.get("/blocked")
def get_blocked_missions(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    return get_blocked_missions_data(
        db=db,
        workspace_id=workspace_id
    )


# =========================
# AGENT ANALYTICS
# =========================

@router.get("/agents")
def get_agent_analytics(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    return get_agent_analytics_data(
        db=db,
        workspace_id=workspace_id
    )


# =========================
# ANALYTICS OVERVIEW
# =========================

@router.get("/overview")
def get_analytics_overview(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    return get_analytics_overview_data(
        db=db,
        workspace_id=workspace_id
    )