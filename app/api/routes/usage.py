from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db

from app.models.usage import Usage
from app.models.agent import Agent
from app.models.user import User

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

router = APIRouter(
    prefix="/usage",
    tags=["Usage"]
)


# =========================
# USAGE OVERVIEW
# =========================

@router.get("/overview")
def get_usage_overview(

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

    agent_ids = db.query(
        Agent.id
    ).filter(
        Agent.workspace_id ==
        workspace_id
    ).all()

    agent_ids = [
        agent[0]
        for agent in agent_ids
    ]

    # TOTAL LOGS

    total_logs = db.query(
        Usage
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).count()

    # TOTAL COST

    total_cost = db.query(
        func.sum(Usage.cost)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    # TOTAL PROMPT TOKENS

    prompt_tokens = db.query(
        func.sum(Usage.prompt_tokens)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    # TOTAL COMPLETION TOKENS

    completion_tokens = db.query(
        func.sum(Usage.completion_tokens)
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).scalar() or 0

    # TOTAL TOKENS

    total_tokens = (
        prompt_tokens +
        completion_tokens
    )

    return {

        "total_logs":
            total_logs,

        "total_cost":
            round(total_cost, 4),

        "prompt_tokens":
            prompt_tokens,

        "completion_tokens":
            completion_tokens,

        "total_tokens":
            total_tokens
    }


# =========================
# LIVE USAGE FEED
# =========================

@router.get("/feed")
def get_usage_feed(

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

    agent_ids = db.query(
        Agent.id
    ).filter(
        Agent.workspace_id ==
        workspace_id
    ).all()

    agent_ids = [
        agent[0]
        for agent in agent_ids
    ]

    # GET RECENT LOGS

    logs = db.query(
        Usage
    ).filter(
        Usage.agent_id.in_(agent_ids)
    ).order_by(
        Usage.timestamp.desc()
    ).limit(50).all()

    return [

        {

            "id":
                log.id,

            "agent_id":
                log.agent_id,

            "step_id":
                log.step_id,

            "action":
                log.action,

            "prompt_tokens":
                log.prompt_tokens,

            "completion_tokens":
                log.completion_tokens,

            "total_tokens":
                (
                    log.prompt_tokens or 0
                ) + (
                    log.completion_tokens or 0
                ),

            "cost":
                log.cost,

            "usage_events":
                log.usage_events,

            "timestamp":
                log.timestamp
        }

        for log in logs
    ]


# =========================
# STEP USAGE DETAILS
# =========================

@router.get("/step/{step_id}")
def get_step_usage(

    step_id: str,

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

    # GET STEP LOGS

    logs = db.query(
        Usage
    ).filter(
        Usage.step_id == step_id
    ).order_by(
        Usage.timestamp.desc()
    ).all()

    # NOT FOUND

    if not logs:

        raise HTTPException(
            status_code=404,
            detail="Usage logs not found"
        )

    return [

        {

            "id":
                log.id,

            "agent_id":
                log.agent_id,

            "step_id":
                log.step_id,

            "action":
                log.action,

            "prompt_tokens":
                log.prompt_tokens,

            "completion_tokens":
                log.completion_tokens,

            "total_tokens":
                (
                    log.prompt_tokens or 0
                ) + (
                    log.completion_tokens or 0
                ),

            "cost":
                log.cost,

            "usage_events":
                log.usage_events,

            "timestamp":
                log.timestamp
        }

        for log in logs
    ]