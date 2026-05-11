from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db

from app.models.agent import Agent
from app.models.durable_step import DurableStep
from app.models.usage import Usage
from app.models.user import User

from app.api.deps_user import get_current_user


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/costs")
def get_cost_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    # Get all user agents
    user_agents = db.query(Agent).filter(
        Agent.user_id == current_user.id
    ).all()

    agent_ids = [
        agent.id
        for agent in user_agents
    ]

    # Total steps
    total_steps = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids)
    ).count()

    # Total cost
    total_cost = db.query(
        func.sum(Usage.cost)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    # Average cost
    average_cost = (
        total_cost / total_steps
        if total_steps > 0
        else 0
    )

    return {
        "total_steps": total_steps,
        "total_cost": round(total_cost, 4),
        "average_cost": round(
            average_cost,
            6
        ),
    }


@router.get("/blocked")
def get_blocked_missions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    user_agents = db.query(Agent).filter(
        Agent.user_id == current_user.id
    ).all()

    agent_ids = [
        agent.id
        for agent in user_agents
    ]

    blocked = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(
            agent_ids
        ),
        DurableStep.status == "blocked"
    ).count()

    return {
        "blocked_missions": blocked
    }


@router.get("/agents")
def get_agent_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    total_agents = db.query(
        Agent
    ).filter(
        Agent.user_id == current_user.id
    ).count()

    return {
        "total_agents": total_agents
    }