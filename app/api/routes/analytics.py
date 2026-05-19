from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db

from app.models.agent import Agent
from app.models.durable_step import DurableStep
from app.models.usage import Usage
from app.models.user import User

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# =========================
# COST ANALYTICS
# =========================

@router.get("/costs")
def get_cost_analytics(

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

    # GET WORKSPACE AGENTS

    user_agents = db.query(Agent).filter(
        Agent.workspace_id ==
        workspace_id
    ).all()

    agent_ids = [
        agent.id
        for agent in user_agents
    ]

    # TOTAL STEPS

    total_steps = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids)
    ).count()

    # TOTAL COST

    total_cost = db.query(
        func.sum(Usage.cost)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    # AVERAGE COST

    average_cost = (
        total_cost / total_steps
        if total_steps > 0
        else 0
    )

    return {

        "total_steps":
            total_steps,

        "total_cost":
            round(total_cost, 4),

        "average_cost":
            round(
                average_cost,
                6
            )
    }


# =========================
# BLOCKED MISSIONS
# =========================

@router.get("/blocked")
def get_blocked_missions(

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

    # GET WORKSPACE AGENTS

    user_agents = db.query(Agent).filter(
        Agent.workspace_id ==
        workspace_id
    ).all()

    agent_ids = [
        agent.id
        for agent in user_agents
    ]

    # BLOCKED MISSIONS

    blocked = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(
            agent_ids
        ),

        DurableStep.status ==
        "blocked"
    ).count()

    return {

        "blocked_missions":
            blocked
    }


# =========================
# AGENT ANALYTICS
# =========================

@router.get("/agents")
def get_agent_analytics(

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

    # TOTAL AGENTS

    total_agents = db.query(
        Agent
    ).filter(
        Agent.workspace_id ==
        workspace_id
    ).count()

    return {

        "total_agents":
            total_agents
    }


# =========================
# ANALYTICS OVERVIEW
# =========================

@router.get("/overview")
def get_analytics_overview(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # =========================
    # VALIDATE MEMBERSHIP
    # =========================

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # =========================
    # GET WORKSPACE AGENTS
    # =========================

    user_agents = db.query(Agent).filter(
        Agent.workspace_id == workspace_id
    ).all()

    agent_ids = [
        agent.id
        for agent in user_agents
    ]

    # =========================
    # TOTAL AGENTS
    # =========================

    total_agents = len(user_agents)

    # =========================
    # TOTAL STEPS
    # =========================

    total_steps = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids)
    ).count()

    # =========================
    # BLOCKED MISSIONS
    # =========================

    blocked_missions = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids),

        DurableStep.status == "blocked"
    ).count()

    # =========================
    # SUCCESSFUL STEPS
    # =========================

    successful_steps = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids),

        DurableStep.status == "completed"
    ).count()

    # =========================
    # FAILED STEPS
    # =========================

    failed_steps = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids),

        DurableStep.status == "failed"
    ).count()

    # =========================
    # TOTAL COST
    # =========================

    total_cost = db.query(
        func.sum(Usage.cost)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    # =========================
    # TOKEN ANALYTICS
    # =========================

    total_prompt_tokens = db.query(
        func.sum(Usage.prompt_tokens)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    total_completion_tokens = db.query(
        func.sum(Usage.completion_tokens)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    total_tokens = (
        total_prompt_tokens +
        total_completion_tokens
    )

    # =========================
    # CACHE ANALYTICS
    # =========================

    cache_hits = db.query(
        DurableStep
    ).filter(
        DurableStep.agent_id.in_(agent_ids),

        DurableStep.cache_hit == True
    ).count()

    cache_misses = (
        total_steps - cache_hits
    )

    # =========================
    # SUCCESS RATE
    # =========================

    success_rate = (
        (successful_steps / total_steps) * 100
        if total_steps > 0
        else 0
    )

    # =========================
    # CACHE HIT RATE
    # =========================

    cache_hit_rate = (
        (cache_hits / total_steps) * 100
        if total_steps > 0
        else 0
    )

    # =========================
    # AVERAGE COST
    # =========================

    average_cost = (
        total_cost / total_steps
        if total_steps > 0
        else 0
    )

    # =========================
    # RECENT USAGE LOGS
    # =========================

    recent_logs = db.query(
        Usage
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).order_by(
        Usage.timestamp.desc()
    ).limit(10).all()

    logs = []

    for log in recent_logs:

        logs.append({

            "id":
                log.id,

            "agent_id":
                log.agent_id,

            "step_id":
                log.step_id,

            "action":
                log.action,

            "cost":
                log.cost,

            "prompt_tokens":
                log.prompt_tokens,

            "completion_tokens":
                log.completion_tokens,

            "timestamp":
                str(log.timestamp)
        })

    # =========================
    # FINAL RESPONSE
    # =========================

    return {

        "overview": {

            "total_agents":
                total_agents,

            "total_steps":
                total_steps,

            "blocked_missions":
                blocked_missions,

            "successful_steps":
                successful_steps,

            "failed_steps":
                failed_steps,

            "success_rate":
                round(success_rate, 2)
        },

        "costs": {

            "total_cost":
                round(total_cost, 4),

            "average_cost":
                round(average_cost, 6)
        },

        "tokens": {

            "prompt_tokens":
                total_prompt_tokens,

            "completion_tokens":
                total_completion_tokens,

            "total_tokens":
                total_tokens
        },

        "cache": {

            "cache_hits":
                cache_hits,

            "cache_misses":
                cache_misses,

            "cache_hit_rate":
                round(cache_hit_rate, 2)
        },

        "live_feed":
            logs
    }