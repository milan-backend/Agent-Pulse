# ============================================
# app/services/analytics_service.py
# ============================================

from fastapi import HTTPException

from sqlalchemy import func

from app.models.agent import Agent
from app.models.workspace import Workspace
from app.models.durable_step import DurableStep
from app.models.usage import Usage

from app.services.feature_access import (
    require_feature
)


# ============================================
# VALIDATE ANALYTICS ACCESS
# ============================================

def validate_analytics_access(
    db,
    workspace_id
):

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

    require_feature(
        workspace,
        "analytics"
    )

    return workspace


# ============================================
# GET WORKSPACE AGENT IDS
# ============================================

def get_workspace_agent_ids(
    db,
    workspace_id
):

    agents = (
        db.query(Agent)
        .filter(
            Agent.workspace_id == workspace_id
        )
        .all()
    )

    return [agent.id for agent in agents]


# ============================================
# COST ANALYTICS
# ============================================

def get_cost_analytics_data(
    db,
    workspace_id
):

    validate_analytics_access(
        db,
        workspace_id
    )

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    total_steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids)
        )
        .count()
    )

    total_cost = (
        db.query(
            func.sum(Usage.cost)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )

    average_cost = (
        total_cost / total_steps
        if total_steps > 0
        else 0
    )

    return {

        "total_steps":
            total_steps,

        "total_cost":
            round(total_cost, 8),

        "average_cost":
            round(average_cost, 8)
    }


# ============================================
# BLOCKED MISSIONS
# ============================================

def get_blocked_missions_data(
    db,
    workspace_id
):

    validate_analytics_access(
        db,
        workspace_id
    )

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    blocked = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids),

            DurableStep.status == "failed"
        )
        .count()
    )

    return {

        "blocked_missions":
            blocked
    }


# ============================================
# AGENT ANALYTICS
# ============================================

def get_agent_analytics_data(
    db,
    workspace_id
):

    validate_analytics_access(
        db,
        workspace_id
    )

    total_agents = (
        db.query(Agent)
        .filter(
            Agent.workspace_id == workspace_id
        )
        .count()
    )

    return {

        "total_agents":
            total_agents
    }


# ============================================
# ANALYTICS OVERVIEW
# ============================================

def get_analytics_overview_data(
    db,
    workspace_id
):

    validate_analytics_access(
        db,
        workspace_id
    )

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    total_agents = len(agent_ids)

    total_steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids)
        )
        .count()
    )

    blocked_missions = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids),

            DurableStep.status == "failed"
        )
        .count()
    )

    successful_steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids),

            DurableStep.status == "completed"
        )
        .count()
    )

    failed_steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids),

            DurableStep.status == "failed"
        )
        .count()
    )

    total_cost = (
        db.query(
            func.sum(Usage.cost)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )

    total_prompt_tokens = (
        db.query(
            func.sum(Usage.prompt_tokens)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )

    total_completion_tokens = (
        db.query(
            func.sum(Usage.completion_tokens)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )

    total_tokens = (
        total_prompt_tokens +
        total_completion_tokens
    )

    cache_hits = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(agent_ids),

            DurableStep.cache_hit == True
        )
        .count()
    )

    cache_misses = (
        total_steps - cache_hits
    )

    success_rate = (
        (successful_steps / total_steps) * 100
        if total_steps > 0
        else 0
    )

    cache_hit_rate = (
        (cache_hits / total_steps) * 100
        if total_steps > 0
        else 0
    )

    average_cost = (
        total_cost / total_steps
        if total_steps > 0
        else 0
    )

    recent_logs = (
        db.query(Usage)
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .order_by(
            Usage.created_at.desc()
        )
        .limit(10)
        .all()
    )

    logs = []

    for log in recent_logs:

        logs.append({

            "id":
                str(log.id),

            "agent_id":
                str(log.agent_id),

            "step_id":
                str(log.step_id),

            "event_type":
                log.event_type,

            "cost":
                log.cost,

            "prompt_tokens":
                log.prompt_tokens,

            "completion_tokens":
                log.completion_tokens,

            "timestamp":
                str(log.created_at)
        })

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
                round(total_cost, 8),

            "average_cost":
                round(average_cost, 8)
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


# ============================================
# GET TOTAL COST
# ============================================

def get_total_cost(
    db,
    agent_ids
):

    return (
        db.query(
            func.sum(Usage.cost)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )


# ============================================
# GET TOKEN ANALYTICS
# ============================================

def get_token_analytics(
    db,
    agent_ids
):

    prompt_tokens = (
        db.query(
            func.sum(Usage.prompt_tokens)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )

    completion_tokens = (
        db.query(
            func.sum(Usage.completion_tokens)
        )
        .filter(
            Usage.agent_id.in_(agent_ids)
        )
        .scalar()
        or 0
    )

    return {

        "prompt_tokens":
            prompt_tokens,

        "completion_tokens":
            completion_tokens,

        "total_tokens":
            (
                prompt_tokens +
                completion_tokens
            )
    }