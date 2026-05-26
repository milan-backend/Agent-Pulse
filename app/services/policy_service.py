# ============================================
# app/services/policy_service.py
# ============================================

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.workspace import Workspace

from app.services.feature_access import (
    require_feature
)


def validate_policy_feature(
    db,
    workspace_id
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
        "advanced_runtime_controls"
    )


def update_agent_policy(
    db: Session,
    workspace_id: str,
    agent_id: str,
    request
):

    validate_policy_feature(
        db,
        workspace_id
    )

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

    policy = agent.policy

    if not policy:

        raise HTTPException(
            status_code=404,
            detail="Agent policy not found"
        )

    # UPDATE POLICY
    policy.max_steps = (
        request.max_steps
    )

    policy.max_retries = (
        request.max_retries
    )

    policy.max_cost = (
        request.max_cost
    )

    policy.max_repeated_tasks = (
        request.max_repeated_tasks
    )

    db.commit()

    db.refresh(policy)

    return {

        "success": True,

        "message":
            "Budget controls updated successfully",

        "agent_id":
            str(agent.id),

        "limits": {

            "max_steps":
                policy.max_steps,

            "max_retries":
                policy.max_retries,

            "max_cost":
                policy.max_cost,

            "max_repeated_tasks":
                policy.max_repeated_tasks
        }
    }


def validate_agent_policy(
    agent,
    usage_cost: float,
    repeated_tasks: int,
    retry_count: int,
    total_steps: int
):

    policy = agent.policy

    if not policy:
        return

    if (
        policy.enable_budget_control
        and usage_cost > policy.max_cost
    ):

        raise Exception(
            "Max cost exceeded"
        )

    if (
        policy.enable_retry_control
        and retry_count >
        policy.max_retries
    ):

        raise Exception(
            "Max retries exceeded"
        )

    if (
        policy.enable_loop_detection
        and repeated_tasks >
        policy.max_repeated_tasks
    ):

        raise Exception(
            "Repeated task limit exceeded"
        )

    if (
        total_steps >
        policy.max_steps
    ):

        raise Exception(
            "Max steps exceeded"
        )