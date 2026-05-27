from fastapi import HTTPException

from sqlalchemy.sql import func

from app.models.usage import Usage

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.models.plan import Plan

from app.models.billing_event import (
    BillingEvent
)


# ============================================
# CREATE USAGE EVENT
# ============================================

def create_usage_event(

    db,

    workspace_id,

    agent_id,

    step_id,

    event_type,

    status=None,

    model_used=None,

    request_id=None,

    cost=0.0,

    prompt_tokens=0,

    completion_tokens=0,

    latency_ms=None,

    cache_hit=False,

    event_metadata=None
):

    # ============================================
    # FORCE SAFE TYPES
    # ============================================

    cost = float(
        cost or 0.0
    )

    prompt_tokens = int(
        prompt_tokens or 0
    )

    completion_tokens = int(
        completion_tokens or 0
    )

    # ============================================
    # WORKSPACE BILLING CHECK
    # ============================================

    subscription = (

        db.query(
            WorkspaceSubscription
        )
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

            detail=
                "No active subscription"
        )

    plan = (

        db.query(Plan)
        .filter(
            Plan.id ==
            subscription.plan_id
        )
        .first()
    )

    if not plan:

        raise HTTPException(

            status_code=403,

            detail="Invalid plan"
        )

    # ============================================
    # CURRENT WORKSPACE COST
    # ============================================

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
        workspace_total_cost or 0.0
    )

    # ============================================
    # MONTHLY LIMIT
    # ============================================

    max_monthly_cost = (

        plan.limits.get(
            "max_monthly_cost",
            10
        )
    )

    projected_cost = (
        workspace_total_cost + cost
    )

    # ============================================
    # BILLING LIMIT EXCEEDED
    # ============================================

    if projected_cost > max_monthly_cost:

        billing_event = BillingEvent(

            workspace_id=workspace_id,

            agent_id=agent_id,

            step_id=step_id,

            event_type=
                "monthly_limit_exceeded",

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

    # ============================================
    # CREATE USAGE RECORD
    # ============================================

    usage = Usage(

        workspace_id=workspace_id,

        agent_id=agent_id,

        step_id=step_id,

        event_type=event_type,

        status=status,

        model_used=model_used,

        request_id=request_id,

        cost=float(cost),

        prompt_tokens=int(
            prompt_tokens
        ),

        completion_tokens=int(
            completion_tokens
        ),

        total_tokens=(

            int(prompt_tokens)

            +

            int(completion_tokens)
        ),

        latency_ms=latency_ms,

        cache_hit=cache_hit,

        event_metadata=event_metadata
    )

    db.add(usage)

    db.flush()

    return usage