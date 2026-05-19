from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.durable_step import DurableStep
from app.models.user import User

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

router = APIRouter(
    prefix="/missions",
    tags=["Missions"]
)


# =========================
# MISSION OVERVIEW
# =========================

@router.get("/overview")
def mission_overview(

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

    # TOTAL MISSIONS

    total = db.query(
        DurableStep
    ).filter(
        DurableStep.workspace_id ==
        workspace_id
    ).count()

    # RUNNING

    running = db.query(
        DurableStep
    ).filter(
        DurableStep.workspace_id ==
        workspace_id,

        DurableStep.status ==
        "running"
    ).count()

    # COMPLETED

    completed = db.query(
        DurableStep
    ).filter(
        DurableStep.workspace_id ==
        workspace_id,

        DurableStep.status ==
        "completed"
    ).count()

    # FAILED

    failed = db.query(
        DurableStep
    ).filter(
        DurableStep.workspace_id ==
        workspace_id,

        DurableStep.status ==
        "failed"
    ).count()

    # PAUSED

    paused = db.query(
        DurableStep
    ).filter(
        DurableStep.workspace_id ==
        workspace_id,

        DurableStep.paused_at != None
    ).count()

    # RESPONSE

    return {

        "total_missions":
            total,

        "running":
            running,

        "completed":
            completed,

        "failed":
            failed,

        "paused":
            paused
    }


# =========================
# MISSION LIST
# =========================

@router.get("/list")
def list_missions(

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

    # GET MISSIONS

    steps = db.query(
        DurableStep
    ).filter(
        DurableStep.workspace_id ==
        workspace_id
    ).order_by(
        DurableStep.created_at.desc()
    ).limit(50).all()

    # RESPONSE

    return [

        {

            "id":
                step.id,

            "task_name":
                step.task_name,

            "status":
                step.status,

            "agent_id":
                step.agent_id,

            "created_at":
                step.created_at,

            "updated_at":
                step.updated_at,

            "retry_count":
                step.retry_count,

            "cache_hit":
                step.cache_hit,

            "runtime_controlled":
                step.runtime_controlled
        }

        for step in steps
    ]


# =========================
# MISSION DETAIL
# =========================

@router.get("/{step_id}")
def get_mission(

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

    # GET STEP

    step = db.query(
        DurableStep
    ).filter(
        DurableStep.id == step_id,

        DurableStep.workspace_id ==
        workspace_id
    ).first()

    # NOT FOUND

    if not step:

        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    # RESPONSE

    return {

        "id":
            step.id,

        "task_name":
            step.task_name,

        "status":
            step.status,

        "agent_id":
            step.agent_id,

        "input_data":
            step.input_data,

        "output_data":
            step.output_data,

        "retry_count":
            step.retry_count,

        "cache_hit":
            step.cache_hit,

        "event_type":
            getattr(
                step,
                "event_type",
                None
            ),

        "error_message":
            step.error_message,

        "runtime_controlled":
            step.runtime_controlled,

        "created_at":
            step.created_at,

        "updated_at":
            step.updated_at,

        "started_at":
            step.started_at,

        "paused_at":
            step.paused_at,

        "killed_at":
            step.killed_at,

        "resumed_at":
            step.resumed_at,

        "pause_reason":
            step.pause_reason
    }


# =========================
# KILL MISSION
# =========================

@router.post("/{step_id}/kill")
def kill_mission(

    step_id: str
):

    return {

        "message":
            "Kill endpoint coming soon",

        "step_id":
            step_id
    }


# =========================
# RESUME MISSION
# =========================

@router.post("/{step_id}/resume")
def resume_mission(

    step_id: str
):

    return {

        "message":
            "Resume endpoint coming soon",

        "step_id":
            step_id
    }