import uuid

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.agent import Agent
from app.models.durable_step import DurableStep
from app.models.usage import Usage
from app.models.audit_log import AuditLog

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.models.plan import Plan

from app.services.cache import generate_cache_key
from app.services.audit_service import create_audit_log
from app.services.usage_service import create_usage_event
from app.services.guard import evaluate_agent_runtime

from app.tasks.step_tasks import process_step

from app.api.routes.ws import broadcast_message

import json

from datetime import datetime, timedelta

async def create_step_execution(
    db: Session,
    current_agent: Agent,
    request
):

    # ============================================
    # ACTIVE SUBSCRIPTION CHECK
    # ============================================

    subscription = (
        db.query(WorkspaceSubscription)
        .filter(
            WorkspaceSubscription.workspace_id
            == current_agent.workspace_id,

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

    # ============================================
    # TASK ACCESS CONTROL
    # ============================================

    if (
        hasattr(current_agent, "allowed_tasks")
        and current_agent.allowed_tasks
    ):

        if request.task_name not in current_agent.allowed_tasks:

            raise HTTPException(
                status_code=403,
                detail="Access denied: task not allowed"
            )

    # ============================================
    # CURRENT COUNTS
    # ============================================

    current_step_count = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id
            == current_agent.id
        )
        .count()
    )

    current_retry_count = 0

    five_minutes_ago = datetime.utcnow()
    -timedelta(minutes=5)

    repeated_task_count = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id
            == current_agent.id,

            DurableStep.task_name
            == request.task_name,

            DurableStep.created_at >= five_minutes_ago
        )
        .count()
    )

    # ============================================
    # AGENT POLICY
    # ============================================

    policy = current_agent.policy

    if not policy:

        raise HTTPException(
            status_code=500,
            detail="Agent policy missing"
        )

    # ============================================
    # CURRENT TOTAL COST
    # ============================================

    agent_total_cost = (
        db.query(Usage)
        .filter(
            Usage.agent_id ==
            current_agent.id
        )
        .with_entities(
            Usage.cost
        )
        .all()
    )

    agent_total_cost = sum(
        item.cost or 0
        for item in agent_total_cost
    )

    # ============================================
    # RUNTIME GUARD
    # ============================================

    guard = evaluate_agent_runtime(

        total_steps=current_step_count,

        retry_count=current_retry_count,

        total_cost=agent_total_cost,

        repeated_task_count=repeated_task_count,

        execution_time_seconds=0,

        max_steps=policy.max_steps,

        max_retries=policy.max_retries,

        max_cost=policy.max_cost,

        max_repeated_tasks=policy.max_repeated_tasks,

        max_execution_time_seconds=
            policy.max_execution_time_seconds,

        enable_budget_control=
            policy.enable_budget_control,

        enable_retry_control=
            policy.enable_retry_control,

        enable_loop_detection=
            policy.enable_loop_detection,
    )

    if guard["stop"]:

       failed_step = DurableStep(
        agent_id=current_agent.id,
        workspace_id=current_agent.workspace_id,
        task_name=request.task_name,
        input_data=request.input_data,
        status="failed",
        error_message=guard["reason"],
        runtime_controlled=True,
        idempotency_key=request.idempotency_key
    )

       db.add(failed_step)
       db.flush()

       create_usage_event(
         db=db,
         workspace_id=current_agent.workspace_id,
         agent_id=current_agent.id,
         step_id=failed_step.id,
         event_type="execution_failed"
    )

       db.commit()

       raise HTTPException(
        status_code=429,
        detail=f"Agent stopped: {guard['reason']}"
    )

    # ============================================
    # IDEMPOTENCY
    # ============================================

    existing = None

    if policy.enable_idempotency:

        existing = (
            db.query(DurableStep)
            .filter(
                DurableStep.idempotency_key ==
                request.idempotency_key,

                DurableStep.workspace_id ==
                current_agent.workspace_id
            )
            .first()
        )

    if existing:

        create_usage_event(
            db=db,
            agent_id=current_agent.id,
            workspace_id=current_agent.workspace_id,
            step_id=existing.id,
            event_type="cache_hit"
        )

        db.commit()

        return {
            "message": "Already exists",
            "step_id": existing.id,
            "status": existing.status,
            "output": existing.output_data,
            "error": existing.error_message
        }

    # ============================================
    # REFRESH AGENT
    # ============================================

    db.refresh(current_agent)

    if current_agent.status == "killed":

        raise HTTPException(
            status_code=409,
            detail="Agent manually stopped"
        )

    # ============================================
    # CONCURRENT EXECUTION LIMIT
    # ============================================

    running_steps = (
        db.query(
            func.count(DurableStep.id)
        )
        .filter(
            DurableStep.workspace_id
            == current_agent.workspace_id,

            DurableStep.status.in_([
                "pending",
                "running"
            ])
        )
        .scalar()
    )

    max_parallel_runs = (
        plan.limits.get(
            "max_concurrent_runs",
            1
        )
    )

    if running_steps >= max_parallel_runs:

        raise HTTPException(
            status_code=429,
            detail=(
            f"Concurrent execution limit exceeded."
            f"Running={running_steps},"
            f"Limits={max_parallel_runs}"
            )
        )


    # ============================================
    # CREATE STEP
    # ============================================

    step = DurableStep(

        agent_id=current_agent.id,

        workspace_id=current_agent.workspace_id,

        task_name=request.task_name,

        input_data=request.input_data,

        status="pending",

        idempotency_key=
            request.idempotency_key,

        runtime_controlled=True
    )

    db.add(step)

    db.flush()

    # ============================================
    # CREATE EXECUTION EVENT
    # ============================================

    create_usage_event(

        db=db,

        workspace_id=
            current_agent.workspace_id,

        agent_id=
            current_agent.id,

        step_id=
            step.id,

        event_type=
            "execution_started"
    )

    db.commit()

    # ============================================
    # BACKGROUND TASK
    # ============================================

    process_step.delay(
        str(step.id)
    )

    # ============================================
    # WEBSOCKET EVENT
    # ============================================

    await broadcast_message(

        json.dumps({

            "type":
                "mission_updated"
        })
    )

    return {

        "message":
            "Step scheduled",

        "step_id":
            step.id,

        "status":
            "pending"
    }


def retry_failed_step(
    db: Session,
    current_agent: Agent,
    step_id: str
):

    step = (
        db.query(DurableStep)
        .filter(
            DurableStep.id == step_id,

            DurableStep.agent_id
            == current_agent.id
        )
        .first()
    )

    if not step:

        raise HTTPException(
            status_code=404,
            detail="Step not found"
        )

    if step.status != "failed":

        raise HTTPException(
            status_code=409,
            detail="Step is not failed"
        )

    policy = current_agent.policy

    if not policy:

        raise HTTPException(
            status_code=500,
            detail="Agent policy missing"
        )

    if (
        policy.enable_retry_control
        and step.retry_count >=
        policy.max_retries
    ):

        raise HTTPException(
            status_code=429,
            detail="Retry limit exceeded"
        )

    # ============================================
    # USAGE EVENT
    # ============================================

    create_usage_event(

        db=db,

        agent_id=current_agent.id,

        workspace_id=
            current_agent.workspace_id,

        step_id=step.id,

        event_type="retry"
    )

    # ============================================
    # AUDIT LOG
    # ============================================

    create_audit_log(

        db=db,

        workspace_id=
            current_agent.workspace_id,

        user_id=
            current_agent.created_by,

        agent_id=
            current_agent.id,

        action=
            "step_retried"
    )

    # ============================================
    # RESET STEP
    # ============================================

    new_step = DurableStep(
        agent_id=step.agent_id,

        workspace_id=step.workspace_id,

        task_name=step.task_name,
        
        input_data=step.input_data,

        status="pending",

        runtime_controlled=True,

        retry_of_step_id=step.id,

        idempotency_key=str(uuid.uuid4())
    )

    db.add(new_step)
    
    db.commit()

    # ============================================
    # BACKGROUND TASK
    # ============================================

    process_step.delay(
        str(new_step.id)
    )

    return {

        "message":
            "Retry scheduled",

        "step_id":
            new_step.id
    }


async def get_step_execution_status(
    db,
    current_agent,
    step_id: str
):

    step = (
        db.query(DurableStep)
        .filter(
            DurableStep.id == step_id,

            DurableStep.agent_id
            == current_agent.id
        )
        .first()
    )

    if not step:

        raise HTTPException(
            status_code=404,
            detail="Step not found"
        )

    return {

        "step_id":
            step.id,

        "status":
            step.status,

        "input_data":
            step.input_data,

        "output_data":
            step.output_data,

        "error_message":
            step.error_message,

        "prompt_tokens":
            step.prompt_tokens,

        "completion_tokens":
            step.completion_tokens,

        "total_tokens":
            getattr(
                step,
                "total_tokens",
                0
            ),

        "started_at":
            (
                str(step.started_at)
                if step.started_at
                else None
            ),

        "completed_at":
            (
                str(step.completed_at)
                if step.completed_at
                else None
            ),

        "created_at":
            (
                str(step.created_at)
                if step.created_at
                else None
            )
    }