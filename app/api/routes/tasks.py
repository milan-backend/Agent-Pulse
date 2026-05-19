from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.durable_step import (
    DurableStep
)

from app.models.user import User

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

router = APIRouter()


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

        "success": True,

        "agent_id": agent_id,

        "workspace_id": workspace_id,

        "count": len(steps),

        "tasks": [

            {

                "step_id":
                    step.id,

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
                    step.event_type,

                "started_at":
                    step.started_at,

                "created_at":
                    step.created_at,

                "updated_at":
                    step.updated_at

            }

            for step in steps
        ]
    }