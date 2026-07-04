import uuid
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps_user import get_current_user
from app.core.workspace_access import get_workspace_membership
from app.db.session import get_db
from app.models.usage import Usage
from app.models.user import User
from app.models.workspace import Workspace
from app.services.analytics_service import (
    get_token_analytics,
    get_total_cost,
    get_workspace_agent_ids,
)
from app.services.feature_access import require_feature
from app.utils.audit_handler import AuditLogRoute

router = APIRouter(route_class=AuditLogRoute)


# ============================================
# VALIDATE USAGE ACCESS
# ============================================
def validate_usage_access(db, workspace_id):
    workspace = (
        db.query(Workspace).filter(Workspace.id == workspace_id).first()
    )

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_feature(workspace, "usage_logs")


# ============================================
# USAGE OVERVIEW
# ============================================
@router.get("/overview")
def get_usage_overview(
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # VALIDATE MEMBERSHIP
    get_workspace_membership(
        db=db, user_id=current_user.id, workspace_id=workspace_id
    )

    validate_usage_access(db, workspace_id)

    # GET WORKSPACE AGENTS
    agent_ids = get_workspace_agent_ids(db, workspace_id)

    # TOTAL LOGS
    total_logs = db.query(Usage).filter(Usage.agent_id.in_(agent_ids)).count()

    # TOTAL COST
    total_cost = get_total_cost(db, agent_ids)

    # TOKEN ANALYTICS
    token_data = get_token_analytics(db, agent_ids)

    return {
        "total_logs": total_logs,
        "total_cost": round(total_cost, 4),
        "prompt_tokens": token_data["prompt_tokens"],
        "completion_tokens": token_data["completion_tokens"],
        "total_tokens": token_data["total_tokens"],
    }


# ============================================
# LIVE USAGE FEED (UPDATED WITH MULTI-FIELD SEARCH)
# ============================================
@router.get("/feed")
def get_usage_feed(
    workspace_id: str = Header(...),
    q: str = None,  # Optional search parameter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # VALIDATE MEMBERSHIP
    get_workspace_membership(
        db=db, user_id=current_user.id, workspace_id=workspace_id
    )

    validate_usage_access(db, workspace_id)

    # GET WORKSPACE AGENTS
    agent_ids = get_workspace_agent_ids(db, workspace_id)

    # BASE QUERY
    query = db.query(Usage).filter(Usage.agent_id.in_(agent_ids))

    # CASE-INSENSITIVE FIELD EVALUATION
    if q:
        search_filter = f"%{q}%"
        conditions = [Usage.event_type.ilike(search_filter)]

        try:
            uuid.UUID(q)
            conditions.append(Usage.agent_id == q)
            conditions.append(Usage.step_id == q)
            conditions.append(Usage.id == q)
        except ValueError:
            pass

        query = query.filter(or_(*conditions))

    # GET RECENT LOGS
    logs = query.order_by(Usage.created_at.desc()).limit(50).all()

    return [
        {
            "id": str(log.id),
            "agent_id": str(log.agent_id),
            "step_id": str(log.step_id),
            "event_type": log.event_type,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "total_tokens": (
                (log.prompt_tokens or 0) + (log.completion_tokens or 0)
            ),
            "cost": log.cost,
            "created_at": str(log.created_at),
        }
        for log in logs
    ]


# ============================================
# STEP USAGE DETAILS
# ============================================
@router.get("/step/{step_id}")
def get_step_usage(
    step_id: str,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # VALIDATE MEMBERSHIP
    get_workspace_membership(
        db=db, user_id=current_user.id, workspace_id=workspace_id
    )

    validate_usage_access(db, workspace_id)

    # GET STEP LOGS
    logs = (
        db.query(Usage)
        .filter(Usage.step_id == step_id)
        .order_by(Usage.created_at.desc())
        .all()
    )

    if not logs:
        raise HTTPException(status_code=404, detail="Usage logs not found")

    return [
        {
            "id": str(log.id),
            "agent_id": str(log.agent_id),
            "step_id": str(log.step_id),
            "event_type": log.event_type,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "total_tokens": (
                (log.prompt_tokens or 0) + (log.completion_tokens or 0)
            ),
            "cost": log.cost,
            "created_at": str(log.created_at),
        }
        for log in logs
    ]