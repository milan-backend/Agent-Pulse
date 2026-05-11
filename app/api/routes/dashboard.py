from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.agent import Agent
from app.models.durable_step import DurableStep
from app.models.usage import Usage

from app.api.deps_user import get_current_user

router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_steps = db.query(DurableStep).filter(
          DurableStep.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
)
    ).count()

    completed = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
),
        DurableStep.status == "completed"
    ).count()

    failed = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
),
        DurableStep.status == "failed"
    ).count()

    pending = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
),
        DurableStep.status.in_(["pending", "running"])
    ).count()

    success_rate = (
        (completed / total_steps) * 100
        if total_steps > 0 else 0 
    )

    return {
        "total_steps": total_steps,
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "success_rate": round(success_rate,2)
    }

@router.get("/usage")
def usage_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.usage import Usage

    total_calls = db.query(Usage).filter(
        Usage.agent_id.in_(
        db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
)
    ).count()

    executions = db.query(Usage).filter(
        Usage.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
),
        Usage.action == "execute"
    ).count()

    retries = db.query(Usage).filter(
        Usage.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
),
        Usage.action == "retry"
    ).count()

    cache_hits = db.query(Usage).filter(
        Usage.agent_id.in_(
          db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
),
        Usage.action == "cache_hit"
    ).count()

    return {
        "total_calls": total_calls,
        "executions": executions,
        "retries": retries,
        "cache_hits": cache_hits
    }

@router.get("/steps")
def list_steps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    steps = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
         db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    )
)
    ).limit(20).all()

    return steps



@router.get("/usage")
def usage_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.usage import Usage

    agent_ids = db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    ).all()

    agent_ids = [a[0] for a in agent_ids]

    records = db.query(Usage).filter(
        Usage.agent_id.in_(agent_ids)
    ).order_by(Usage.timestamp.desc()).all()

    return records


@router.get("/usage/logs")
def usage_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.usage import Usage

    agent_ids = db.query(Agent.id).filter(
        Agent.user_id == current_user.id
    ).all()

    agent_ids = [a[0] for a in agent_ids]

    logs = db.query(Usage).filter(
        Usage.agent_id.in_(agent_ids)
    ).order_by(Usage.timestamp.desc()).limit(50).all()

    return logs