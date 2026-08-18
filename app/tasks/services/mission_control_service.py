# ============================================
# app/services/mission_control_service.py
# ============================================

from datetime import datetime

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.agent import Agent


# ============================================
# GET AGENT
# ============================================

def get_workspace_agent(
    db: Session,
    workspace_id: str,
    agent_id: str
):

    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.workspace_id == workspace_id
        )
        .first()
    )

    if not agent:

        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return agent


# ============================================
# KILL AGENT
# ============================================

def kill_agent_runtime(
    db: Session,
    workspace_id: str,
    agent_id: str,
    current_user
):

    agent = get_workspace_agent(
        db,
        workspace_id,
        agent_id
    )

    agent.status = "killed"

    agent.is_active = False

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
            str(agent.id),

        "workspace_id":
            workspace_id,

        "controlled_by":
            current_user.email,

        "status":
            "killed"
    }


# ============================================
# PAUSE AGENT
# ============================================

def pause_agent_runtime(
    db: Session,
    workspace_id: str,
    agent_id: str,
    current_user
):

    agent = get_workspace_agent(
        db,
        workspace_id,
        agent_id
    )

    agent.status = "paused"

    agent.is_active = False

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
            str(agent.id),

        "workspace_id":
            workspace_id,

        "controlled_by":
            current_user.email,

        "status":
            "paused"
    }


# ============================================
# RESUME AGENT
# ============================================

def resume_agent_runtime(
    db: Session,
    workspace_id: str,
    agent_id: str,
    current_user
):

    agent = get_workspace_agent(
        db,
        workspace_id,
        agent_id
    )

    agent.status = "active"

    agent.is_active = True

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
            str(agent.id),

        "workspace_id":
            workspace_id,

        "controlled_by":
            current_user.email,

        "status":
            "active"
    }