from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.workspace import Workspace

from app.models.durable_step import (
    DurableStep
)

from app.models.user import User

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.services.feature_access import (
    require_feature
)

router = APIRouter()


# ============================================
# VALIDATE TASK ACCESS
# ============================================

def validate_task_access(
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
        "audit_logs"
    )


# ============================================
# GET AGENT TASKS
# ============================================

@router.get("/agent/{agent_id}")
def get_agent_tasks(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE WORKSPACE ACCESS

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    if not membership:

        raise HTTPException(
            status_code=403,
            detail="Workspace access denied"
        )

    validate_task_access(
        db,
        workspace_id
    )

    # FETCH TASKS

    steps = (

        db.query(DurableStep)

        .filter(
            DurableStep.agent_id
            == agent_id,

            DurableStep.workspace_id
            == workspace_id
        )

        .order_by(
            DurableStep.created_at.desc()
        )

        .all()
    )

    return {

        "success":
            True,

        "agent_id":
            str(agent_id),

        "workspace_id":
            str(workspace_id),

        "count":
            len(steps),

        "tasks": [

            {

                "step_id":
                    str(step.id),

                "task_name":
                    step.task_name,

                "status":
                    step.status,

                "input_data":
                    step.input_data,

                "output_data":
                    step.output_data,

                "error_message":
                    step.error_message,

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

                "started_at":
                    str(step.started_at)
                    if step.started_at
                    else None,

                "created_at":
                    str(step.created_at)
                    if step.created_at
                    else None,

                "updated_at":
                    str(step.updated_at)
                    if step.updated_at
                    else None

            }

            for step in steps
        ]
    }