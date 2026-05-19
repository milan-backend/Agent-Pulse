from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.agent import Agent
from app.models.durable_step import DurableStep
from app.models.usage import Usage

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

router = APIRouter()


# =========================
# DASHBOARD SUMMARY
# =========================

@router.get("/summary")
def dashboard_summary(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    total_steps = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        )
    ).count()

    completed = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        ),
        DurableStep.status == "completed"
    ).count()

    failed = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        ),
        DurableStep.status == "failed"
    ).count()

    pending = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        ),
        DurableStep.status.in_([
            "pending",
            "running"
        ])
    ).count()

    success_rate = (
        (completed / total_steps) * 100
        if total_steps > 0
        else 0
    )

    return {

        "total_steps":
            total_steps,

        "completed":
            completed,

        "failed":
            failed,

        "pending":
            pending,

        "success_rate":
            round(
                success_rate,
                2
            )
    }


# =========================
# USAGE SUMMARY
# =========================

@router.get("/usage")
def usage_summary(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    total_calls = db.query(Usage).filter(
        Usage.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        )
    ).count()

    executions = db.query(Usage).filter(
        Usage.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        ),
        Usage.action == "execute"
    ).count()

    retries = db.query(Usage).filter(
        Usage.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        ),
        Usage.action == "retry"
    ).count()

    cache_hits = db.query(Usage).filter(
        Usage.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        ),
        Usage.action == "cache_hit"
    ).count()

    return {

        "total_calls":
            total_calls,

        "executions":
            executions,

        "retries":
            retries,

        "cache_hits":
            cache_hits
    }


# =========================
# LIST STEPS
# =========================

@router.get("/steps")
def list_steps(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    steps = db.query(DurableStep).filter(
        DurableStep.agent_id.in_(
            db.query(Agent.id).filter(
                Agent.workspace_id ==
                workspace_id
            )
        )
    ).limit(20).all()

    return steps


# =========================
# USAGE LOGS
# =========================

@router.get("/usage/logs")
def usage_logs(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    agent_ids = db.query(Agent.id).filter(
        Agent.workspace_id ==
        workspace_id
    ).all()

    agent_ids = [a[0] for a in agent_ids]

    logs = db.query(Usage).filter(
        Usage.agent_id.in_(agent_ids)
    ).order_by(
        Usage.timestamp.desc()
    ).limit(50).all()

    return logs


# =========================
# SINGLE AGENT DETAILS
# =========================

@router.get("/agent/{agent_id}")
def get_agent_by_id(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # FIND AGENT

    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,

            Agent.workspace_id ==
            workspace_id
        )
        .first()
    )

    # NOT FOUND

    if not agent:

        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    # TOTAL MISSIONS

    mission_count = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id ==
            agent.id
        )
        .count()
    )

    # USAGE RECORDS

    steps = (
        db.query(Usage)
        .filter(
            Usage.agent_id ==
            agent.id
        )
        .all()
    )

    # TOTAL COST

    total_cost = 0

    for step in steps:

        if step.cost:

            total_cost += (
                step.cost
            )

    return {

        "id":
            str(agent.id),

        "name":
            agent.name,

        "is_active":
            agent.is_active,

        "is_killed":
            agent.is_killed,

        "max_cost":
            agent.max_cost,

        "max_steps":
            agent.max_steps,

        "max_retries":
            agent.max_retries,

        "max_repeated_tasks":
            agent.max_repeated_tasks,

        "mission_count":
            mission_count,

        "total_cost":
            total_cost,

        "created_at":
            agent.created_at
    }


# =========================
# GET AGENTS
# =========================

@router.get("/agents")
def get_agents(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    agents = (
        db.query(Agent)
        .filter(
            Agent.workspace_id ==
            workspace_id
        )
        .all()
    )

    return {

         "total_agents": len(agents),
         "role" : membership.role,

        "agents": [

            {
                "id":
                    str(agent.id),

                "name":
                    agent.name
            }

            for agent in agents
        ]
    }