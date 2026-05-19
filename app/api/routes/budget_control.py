from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.agent import Agent

from app.api.deps_user import get_current_user

from app.api.rbac import require_admin

router = APIRouter()


@router.put("/update-budget/{agent_id}")
def update_budget_controls(
    agent_id: str,
    max_steps: int,
    max_retries: int,
    max_cost: float,
    max_repeated_tasks: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # RBAC protection
    require_admin(current_user)

    # Find agent
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.workspace_id == current_user.workspace_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    # Update runtime governance limits
    agent.max_steps = max_steps

    agent.max_retries = max_retries

    agent.max_cost = max_cost

    agent.max_repeated_tasks = max_repeated_tasks

    db.commit()

    db.refresh(agent)

    return {
        "success": True,
        "message": "Budget controls updated successfully",
        "agent_id": agent.id,
        "limits": {
            "max_steps": agent.max_steps,
            "max_retries": agent.max_retries,
            "max_cost": agent.max_cost,
            "max_repeated_tasks": agent.max_repeated_tasks
        }
    }