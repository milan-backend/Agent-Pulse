import uuid

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.agent import Agent
from app.models.agent_policy import AgentPolicy

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.models.plan import Plan

from app.models.workspace_usage_limit import (
    WorkspaceUsageLimit
)

from app.core.security import (
    hash_api_key,
    generate_api_key
)


def create_agent_service(
    db: Session,
    workspace_id: str,
    current_user,
    request
):

    # =========================
    # PLAN LIMIT CHECK
    # =========================

    subscription = (
        db.query(WorkspaceSubscription)
        .filter(
            WorkspaceSubscription.workspace_id
            == workspace_id,

            WorkspaceSubscription.status
            == "active"
        )
        .first()
    )

    if not subscription:

        raise HTTPException(
            status_code=403,
            detail="No active subscription"
        )

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not plan:

        raise HTTPException(
            status_code=403,
            detail="Invalid subscription plan"
        )

    current_agent_count = (
        db.query(func.count(Agent.id))
        .filter(
            Agent.workspace_id == workspace_id
        )
        .scalar()
    )

    max_agents = (
        plan.limits.get(
            "max_agents",
            1
        )
    )

    if current_agent_count >= max_agents:

        raise HTTPException(
            status_code=403,
            detail=(
                "Agent limit reached "
                "for current plan"
            )
        )

    # GENERATE API KEY
    api_key, key_id = generate_api_key()

    hashed_key = hash_api_key(
        api_key
    )

    # CREATE AGENT
    agent = Agent(

        id=uuid.uuid4(),

        name=request.name,

        description=request.description,

        api_key_hash=hashed_key,

        key_id=key_id,

        status="active",

        is_active=True,

        created_by=current_user.id,

        workspace_id=workspace_id
    )

    db.add(agent)

    db.flush()

    # CREATE DEFAULT POLICY

    policy = AgentPolicy(

        agent_id=agent.id,

        max_steps=25,

        max_retries=3,

        max_cost=10,

        max_repeated_tasks=3,

        enable_idempotency=True,

        enable_budget_control=True,

        enable_retry_control=True,

        enable_loop_detection=True,

        max_execution_time_seconds=300
    )

    db.add(policy)

    # CREATE WORKSPACE LIMITS
    # IF NOT EXISTS

    existing_limits = (
        db.query(
            WorkspaceUsageLimit
        )
        .filter(
            WorkspaceUsageLimit.workspace_id
            == workspace_id
        )
        .first()
    )

    if not existing_limits:

        limits = WorkspaceUsageLimit(

            workspace_id=workspace_id,

            max_monthly_tokens=100000,

            max_monthly_cost=50,

            max_agents=10,

            max_parallel_runs=5
        )

        db.add(limits)

    db.commit()

    db.refresh(agent)

    return {
        "id": str(agent.id),
        "name": agent.name,
        "api_key": api_key
    }


def regenerate_agent_api_key(
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

    # GENERATE NEW KEY
    raw_api_key, key_id = (
        generate_api_key()
    )

    # UPDATE HASH
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


def update_agent_policy_service(
    db: Session,
    workspace_id: str,
    agent_id: str,
    request
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

    policy = agent.policy

    if not policy:

        raise HTTPException(
            status_code=404,
            detail="Agent policy not found"
        )

    # UPDATE POLICY
    if request.max_steps is not None:

        policy.max_steps = (
            request.max_steps
        )

    if request.max_retries is not None:

        policy.max_retries = (
            request.max_retries
        )

    if request.max_cost is not None:

        policy.max_cost = (
            request.max_cost
        )

    if request.max_repeated_tasks is not None:

        policy.max_repeated_tasks = (
            request.max_repeated_tasks
        )

    db.commit()

    db.refresh(policy)

    return {

        "success": True,

        "message":
            "Agent policy updated",

        "policy": {

            "max_steps":
                policy.max_steps,

            "max_retries":
                policy.max_retries,

            "max_cost":
                policy.max_cost,

            "max_repeated_tasks":
                policy.max_repeated_tasks,

            "enable_idempotency":
                policy.enable_idempotency,

            "enable_budget_control":
                policy.enable_budget_control,

            "enable_retry_control":
                policy.enable_retry_control,

            "enable_loop_detection":
                policy.enable_loop_detection,

            "max_execution_time_seconds":
                policy.max_execution_time_seconds
        }
    }