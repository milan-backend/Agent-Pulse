from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.workspace import Workspace
from app.models.durable_step import DurableStep
from app.models.user import User
from app.models.agent import Agent
from app.models.agent_policy import AgentPolicy
from app.models.usage import Usage

from app.tasks.step_tasks import process_step

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.services.feature_access import (
    require_feature
)

router = APIRouter(
    prefix="/missions",
    tags=["Missions"]
)


# ============================================
# VALIDATE FEATURE ACCESS
# ============================================

def validate_feature_access(
    db,
    workspace_id,
    feature_name
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
        feature_name
    )


# ============================================
# VALIDATE MISSION ACCESS
# ============================================

def validate_mission_access(
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
        "missions"
    )


# ============================================
# MISSION OVERVIEW
# ============================================

@router.get("/overview")
def mission_overview(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # FEATURE

    validate_mission_access(
        db,
        workspace_id
    )

    # TOTAL

    total = (
        db.query(DurableStep)
        .filter(
            DurableStep.workspace_id ==
            workspace_id
        )
        .count()
    )

    # RUNNING

    running = (
        db.query(DurableStep)
        .filter(
            DurableStep.workspace_id ==
            workspace_id,

            DurableStep.status ==
            "running"
        )
        .count()
    )

    # COMPLETED

    completed = (
        db.query(DurableStep)
        .filter(
            DurableStep.workspace_id ==
            workspace_id,

            DurableStep.status ==
            "completed"
        )
        .count()
    )

    # FAILED

    failed = (
        db.query(DurableStep)
        .filter(
            DurableStep.workspace_id ==
            workspace_id,

            DurableStep.status ==
            "failed"
        )
        .count()
    )

    # PAUSED

    paused = (
        db.query(DurableStep)
        .filter(
            DurableStep.workspace_id ==
            workspace_id,

            DurableStep.paused_at != None
        )
        .count()
    )

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


# ============================================
# MISSION LIST
# ============================================

@router.get("/list")
def list_missions(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # FEATURE

    validate_mission_access(
        db,
        workspace_id
    )

    # MISSIONS

    steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.workspace_id ==
            workspace_id
        )
        .order_by(
            DurableStep.created_at.desc()
        )
        .limit(50)
        .all()
    )

    return [

        {

            "mission_id":
                str(step.id),

            "task_name":
                step.task_name,

            "status":
                step.status,

            "agent_id":
                str(step.agent_id),

            "created_at":
                str(step.created_at),

            "updated_at":
                str(step.updated_at),

            "retry_count":
                step.retry_count,

            "cache_hit":
                step.cache_hit,

            "runtime_controlled":
                step.runtime_controlled
        }

        for step in steps
    ]


# ============================================
# MISSION DETAIL
# ============================================

@router.get("/{step_id}")
def get_mission(

    step_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # FEATURE

    validate_mission_access(
        db,
        workspace_id
    )

    # STEP

    step = (
        db.query(DurableStep)
        .filter(
            DurableStep.id == step_id,

            DurableStep.workspace_id ==
            workspace_id
        )
        .first()
    )

    if not step:

        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    return {

        "mission_id":
            str(step.id),

        "task_name":
            step.task_name,

        "status":
            step.status,

        "agent_id":
            str(step.agent_id),

        "retry_count":
            step.retry_count,

        "cache_hit":
            step.cache_hit,

        "runtime_controlled":
            step.runtime_controlled,

        "error_message":
            step.error_message,

        "created_at":
            str(step.created_at),

        "updated_at":
            str(step.updated_at),

        "started_at":
            str(step.started_at)
            if step.started_at
            else None,

        "completed_at":
            str(step.completed_at)
            if step.completed_at
            else None,

        "paused_at":
            str(step.paused_at)
            if step.paused_at
            else None,

        "resumed_at":
            str(step.resumed_at)
            if step.resumed_at
            else None,

        "killed_at":
            str(step.killed_at)
            if step.killed_at
            else None,

        # OPTIONAL SMALL PREVIEW

        "output_preview":
            (
                str(step.output_data)[:120]
                if step.output_data
                else None
            )
    }


# ============================================
# RETRY MISSION
# ============================================

@router.post("/{step_id}/retry")
def retry_mission(

    step_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # ROLE CHECK

    if membership.role not in [
        "admin",
        "operator"
    ]:

        return {
            "error":
            "Insufficient permissions"
        }

    # FEATURE

    validate_mission_access(
        db,
        workspace_id
    )

    # STEP

    step = (
        db.query(DurableStep)
        .filter(
            DurableStep.id == step_id,

            DurableStep.workspace_id ==
            workspace_id
        )
        .first()
    )

    if not step:

        return {
            "error":
            "Mission not found"
        }

    # FAILED CHECK

    if step.status != "failed":

        return {
            "message":
            "Mission is not failed"
        }

    # RESET

    step.status = "pending"

    db.commit()

    process_step.delay(str(step.id))

    return {

        "message":
            "Mission retry scheduled",

        "mission_id":
            str(step.id)
    }


# ============================================
# KILL MISSION
# ============================================

@router.post("/{step_id}/kill")
def kill_mission(

    step_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # ROLE CHECK

    if membership.role not in [
        "admin",
        "operator"
    ]:

        return {
            "error":
            "Insufficient permissions"
        }

    # FEATURE

    validate_mission_access(
        db,
        workspace_id
    )

    return {

        "message":
            "Kill endpoint coming soon",

        "mission_id":
            step_id
    }


# ============================================
# RESUME MISSION
# ============================================

@router.post("/{step_id}/resume")
def resume_mission(

    step_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # ROLE CHECK

    if membership.role not in [
        "admin",
        "operator"
    ]:

        return {
            "error":
            "Insufficient permissions"
        }

    # FEATURE

    validate_mission_access(
        db,
        workspace_id
    )

    return {

        "message":
            "Resume endpoint coming soon",

        "mission_id":
            step_id
    }