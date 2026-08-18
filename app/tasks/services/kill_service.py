# ============================================
# app/services/kill_service.py
# ============================================

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.workspace import Workspace

from app.services.feature_access import (
    require_feature
)


# ============================================
# KILL WORKSPACE AGENTS
# ============================================

def kill_workspace_agents(
    db: Session,
    workspace_id: str,
    current_user
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
        "workspace_kill_all"
    )

    updated_count = (
        db.query(Agent)
        .filter(
            Agent.workspace_id
            == workspace_id
        )
        .update(
            {
                "status": "killed",
                "is_active": False
            },
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


# ============================================
# RESUME WORKSPACE AGENTS
# ============================================

def resume_workspace_agents(
    db: Session,
    workspace_id: str,
    current_user
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
        "workspace_resume_all"
    )

    updated_count = (
        db.query(Agent)
        .filter(
            Agent.workspace_id
            == workspace_id
        )
        .update(
            {
                "status": "active",
                "is_active": True
            },
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