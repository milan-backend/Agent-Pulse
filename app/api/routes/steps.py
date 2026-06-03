from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.durable_step import DurableStep
from app.models.agent import Agent
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.usage import Usage
from app.schemas.step import StepExecuteRequest
from app.api.deps import get_current_agent
from app.api.deps_user import get_current_user
from app.services.step_service import (
    create_step_execution,
    retry_failed_step
)

router = APIRouter()

# ============================================
# EXECUTE STEP
# ============================================
@router.post("/execute")
async def execute_step(
    request: StepExecuteRequest,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    return await create_step_execution(
        db=db,
        current_agent=current_agent,
        request=request
    )

# ============================================
# RETRY FAILED STEP
# ============================================
@router.post("/retry/{step_id}")
def retry_step(
    step_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    return retry_failed_step(
        db=db,
        current_agent=current_agent,
        step_id=step_id
    )

# ============================================
# GET AUDIT LOGS
# ============================================
@router.get("/{step_id}/logs")
def get_step_logs(
    step_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.step_id == str(step_id),
            AuditLog.agent_id == str(current_agent.id)
        )
        .all()
    )
    return logs

# ============================================
# GET USAGE
# ============================================
@router.get("/usage/me")
def get_usage(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    records = (
        db.query(Usage)
        .filter(Usage.agent_id == current_agent.id)
        .all()
    )
    return records

# ============================================
# GET STEP STATUS
# ============================================
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
            Agent.created_by == current_user.id
        )
        .first()
    )

    if not step:
        return {"error": "Step not found"}

    usage_logs = (
        db.query(Usage)
        .filter(Usage.step_id == step.id)
        .order_by(Usage.created_at.desc())
        .all()
    )

    cost = sum(log.cost or 0 for log in usage_logs)
    prompt_tokens = sum(log.prompt_tokens or 0 for log in usage_logs)
    completion_tokens = sum(log.completion_tokens or 0 for log in usage_logs)

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
                "created_at": log.created_at
            }
            for log in usage_logs
        ]
    }
