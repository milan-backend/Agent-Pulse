from fastapi import HTTPException

from sqlalchemy.sql import func

from app.models.usage import Usage

from app.models.workspace import Workspace

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.models.plan import Plan

from app.models.billing_event import (
    BillingEvent
)


def create_usage_event(
    db,
    workspace_id,
    agent_id,
    step_id,
    event_type,
    status=None,
    model_used=None,
    request_id=None,
    cost=0,
    prompt_tokens=0,
    completion_tokens=0,
    latency_ms=None,
    cache_hit=False,
    event_metadata=None
):

    # =========================
    # WORKSPACE BILLING CHECK
    # =========================

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
            detail="Invalid plan"
        )

    # =========================
    # FEATURE ACCESS CHECK
    # =========================

    features = (
        plan.features or {}
    )

    if not features.get(
        "agent_execution",
        False
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Plan does not allow "
                "agent execution"
            )
        )

    # =========================
    # BILLING LIMIT CHECK
    # =========================

    workspace_total_cost = (
        db.query(
            func.sum(Usage.cost)
        )
        .filter(
            Usage.workspace_id ==
            workspace_id
        )
        .scalar()
    )

    workspace_total_cost = float(
        workspace_total_cost or 0
    )

    max_monthly_cost = (
        plan.limits.get(
            "max_monthly_cost",
            10
        )
    )

    projected_cost = (
        workspace_total_cost + cost
    )

    if projected_cost > max_monthly_cost:

        billing_event = BillingEvent(

            workspace_id=workspace_id,

            agent_id=agent_id,

            step_id=step_id,

            event_type="monthly_limit_exceeded",

            amount=projected_cost,

            event_metadata={

                "limit":
                    max_monthly_cost,

                "attempted_cost":
                    projected_cost
            }
        )

        db.add(billing_event)

        db.flush()

        raise HTTPException(

            status_code=403,

            detail=(
                "Workspace monthly "
                "billing limit exceeded"
            )
        )

    # =========================
    # CREATE USAGE EVENT
    # =========================

    usage = Usage(

        workspace_id=workspace_id,

        agent_id=agent_id,

        step_id=step_id,

        event_type=event_type,

        status=status,

        model_used=model_used,

        request_id=request_id,

        cost=cost,

        prompt_tokens=prompt_tokens,

        completion_tokens=completion_tokens,

        total_tokens=(

            prompt_tokens +
            completion_tokens
        ),

        latency_ms=latency_ms,

        cache_hit=cache_hit,

        event_metadata=event_metadata
    )

    db.add(usage)

    db.flush()

    return usage