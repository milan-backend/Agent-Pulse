from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.agent import Agent

from app.models.workspace import Workspace

from app.api.deps import (
    get_current_agent
)

from app.schemas.step import (
    StepExecuteRequest
)

from app.services.step_service import (
    create_step_execution,
    get_step_execution_status
)

from app.services.feature_access import (
    require_feature
)

router = APIRouter()


# ============================================
# MCP TOOL LIST
# ============================================

@router.get("/tools")
def list_tools(

    db: Session = Depends(get_db),

    current_agent: Agent = Depends(
        get_current_agent
    )
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id ==
            current_agent.workspace_id
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
        "mcp_access"
    )

    return {

        "tools": [

            {

                "name":
                    "execute_task",

                "description":
                    "Execute a durable task with reliability",

                "input_schema": {

                    "type":
                        "object",

                    "properties": {

                        "task_name": {
                            "type": "string"
                        },

                        "input_data": {
                            "type": "object"
                        },

                        "idempotency_key": {
                            "type": "string"
                        }
                    },

                    "required": [
                        "task_name",
                        "idempotency_key"
                    ]
                }
            },

            {

                "name":
                    "get_step_status",

                "description":
                    "Check status of a step",

                "input_schema": {

                    "type":
                        "object",

                    "properties": {

                        "step_id": {
                            "type": "string"
                        }
                    },

                    "required": [
                        "step_id"
                    ]
                }
            }
        ]
    }


# ============================================
# MCP EXECUTE TOOL
# ============================================

@router.post("/execute")
async def mcp_execute(

    body: dict = Body(...),

    db: Session = Depends(get_db),

    current_agent: Agent = Depends(
        get_current_agent
    )
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id ==
            current_agent.workspace_id
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
        "mcp_access"
    )

    tool = body.get("tool")

    args = body.get(
        "arguments",
        {}
    )

    # ============================================
    # EXECUTE TASK
    # ============================================

    if tool == "execute_task":

        request = StepExecuteRequest(
            task_name=args.get(
                "task_name"
            ),

            input_data=args.get(
                "input_data",
                {}
            ),

            idempotency_key=args.get(
                "idempotency_key"
            )
        )

        return await create_step_execution(

            db=db,

            current_agent=current_agent,

            request=request
        )

    # ============================================
    # GET STEP STATUS
    # ============================================

    if tool == "get_step_status":

        step_id = args.get(
            "step_id"
        )

        if not step_id:

            raise HTTPException(
                status_code=400,
                detail="step_id is required"
            )

        return await get_step_execution_status(

            db=db,

            current_agent=current_agent,

            step_id=step_id
        )

    # ============================================
    # UNKNOWN TOOL
    # ============================================

    raise HTTPException(
        status_code=400,
        detail="Unknown tool"
    )