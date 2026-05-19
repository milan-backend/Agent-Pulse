from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.db.session import get_db
from app.models.durable_step import DurableStep
from app.models.agent import Agent
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.usage import Usage

from app.schemas.step import StepExecuteRequest

from app.api.deps import get_current_agent

from app.services.execution_engine import execute_task
from app.services.cache import generate_cache_key
from app.services.audit import log_event
from app.services.usage import log_usage
from app.tasks.step_tasks import process_step
from app.api.deps_user import get_current_user
from app.api.routes.ws import broadcast_message
import json
from app.services.guard import should_stop_agent
from app.services.cost import calculate_openai_cost

"""from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))"""

router = APIRouter()


#  EXECUTE STEP (Async + Cache + Idempotency)
@router.post("/execute")
async def execute_step(
    request: StepExecuteRequest,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):

    # 🔐 (Optional ABAC)
    if hasattr(current_agent, "allowed_tasks") and current_agent.allowed_tasks:
        if request.task_name not in current_agent.allowed_tasks:
            return {"error": "Access denied: task not allowed"}
    
    current_step_count = db.query(
       DurableStep).filter(DurableStep.agent_id ==current_agent.id).count()

    current_retry_count = 0

    repeated_task_count = db.query(
            DurableStep
           ).filter(
       DurableStep.agent_id ==current_agent.id,
       DurableStep.task_name ==request.task_name
        ).count()


    """response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user", "content":
            request.task_name
        }
        ]
    )

    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens"""
    prompt_tokens = 800
    completion_tokens = 1200

    total_cost = calculate_openai_cost(
                 prompt_tokens,
                completion_tokens,
)

    guard = should_stop_agent(
              total_steps=current_step_count,
              retry_count=current_retry_count,
              total_cost=total_cost,
              repeated_task_count=repeated_task_count,
              max_steps=current_agent.max_steps,
              max_retries=current_agent.max_retries,
              max_cost=current_agent.max_cost,
              max_repeated_tasks=current_agent.max_repeated_tasks,
)


    if guard["stop"]:
     return {
          "error":
            f"Agent stopped: {guard['reason']}"
    }

    # 🔍 Idempotency check
    existing = db.query(DurableStep).filter(
        DurableStep.idempotency_key == request.idempotency_key
    ).first()

    if existing:

        log_usage(
            db,
            current_agent.id,
            existing.id,
            "cache_hit"
        )

        return {
            "message": "Already exists",
            "step_id": existing.id,
            "status": existing.status,
            "output": existing.output_data,
            "error": existing.error_message
        }

    db.expire_all()
    db.refresh(current_agent)

    if current_agent.is_killed:
        return{
            "error": "Agent manually stopped"
        }
    
    if guard["stop"]:
        return{
            "error": f"Agent stopped:{guard['reason']}"
        }

    # 🚀 Create step
    step = DurableStep(
        agent_id=current_agent.id,
        task_name=request.task_name,
        input_data=request.input_data,
        status="pending",
        idempotency_key=request.idempotency_key,
        workspace_id=current_agent.workspace_id
    )

    db.add(step)
    db.commit()        # 🔥 MUST commit before background task
    db.refresh(step)

    log_usage(db=db, agent_id=current_agent.id,
              step_id=step.id, action="execute", cost=total_cost,prompt_tokens=prompt_tokens,
              completion_tokens=completion_tokens)
    
    
    # 🔥 Background execution
    
    process_step.delay(step.id)

    await broadcast_message(json.dumps({"type": "mission_updated"}))

    return {
        "message": "Step scheduled",
        "step_id": step.id,
        "status": "pending"
    }


# GET STEP STATUS
@router.get("/{step_id}")
def get_step_status(
    step_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    step = (
        db.query(DurableStep)
        .join(Agent, DurableStep.agent_id == Agent.id)
        .filter(
            DurableStep.id == step_id,
            Agent.user_id == current_user.id
        )
        .first()
    )

    print("FOUND STEP:", step)

    if not step:
        return {"error": "Step not found"}

    usage_logs = (
        db.query(Usage)
        .filter(Usage.step_id == step.id)
        .order_by(Usage.timestamp.desc())
        .all()
    )

    cost = sum(
        log.cost or 0
        for log in usage_logs
    )

    prompt_tokens = sum(
        log.prompt_tokens or 0
        for log in usage_logs
    )

    completion_tokens = sum(
        log.completion_tokens or 0
        for log in usage_logs
    )

    return {
        "step_id": step.id,
        "task_name": step.task_name,
        "status": step.status,
        "input": step.input_data,
        "output": step.output_data,
        "error": step.error_message,
        "retry_count": step.retry_count,
        "agent_id": step.agent_id,
        "cache_hit": step.cache_hit,
        "event": step.event_type,
        "created_at": str(step.created_at),
        "updated_at": str(step.updated_at),

        "analytics": {
            "total_cost": round(cost, 6),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "usage_events": len(usage_logs)
        },

        "usage_logs": [
            {
                "cost": log.cost,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "timestamp": log.timestamp
            }
            for log in usage_logs
        ]
    }


#  RETRY FAILED STEP
@router.post("/retry/{step_id}")
def retry_step(
    step_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    step = db.query(DurableStep).filter(
        DurableStep.id == step_id,
        DurableStep.agent_id == current_agent.id
    ).first()

    if not step:
        return {"error": "Step not found"}

    if step.status != "failed":
        return {"message": "Step is not failed"}

    #  Usage tracking
    log_usage(db, current_agent.id, step.id, "retry")

    #  Audit log
    log_event(
        db,
        agent_id=current_agent.id,
        step_id=step.id,
        action="retried"
    )

    #  Reset status
    step.status = "pending"
    db.commit()

    #  Run again in background
    process_step.delay(step.id)

    return {
        "message": "Retry scheduled",
        "step_id": step.id
    }


#  GET AUDIT LOGS
@router.get("/{step_id}/logs")
def get_step_logs(
    step_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    logs = db.query(AuditLog).filter(
        AuditLog.step_id == step_id,
        AuditLog.agent_id == current_agent.id
    ).all()

    return logs


#  GET USAGE (FOR CURRENT AGENT)
@router.get("/usage/me")
def get_usage(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    from app.models.usage import Usage

    records = db.query(Usage).filter(
        Usage.agent_id == current_agent.id
    ).all()

    return records

