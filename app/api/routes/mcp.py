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

import os
import redis
import ssl
import asyncio
from fastapi.responses import StreamingResponse

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

# ============================================
# REAL-TIME TOKEN STREAMING ROUTE
# ============================================

@router.get("/stream/{step_id}")
async def mcp_stream_tokens(
    step_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """
    Subscribes to the live Redis Pub/Sub channel for a given step_id
    and flushes incoming Gemini tokens directly to the user's browser.
    """
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == current_agent.workspace_id)
        .first()
    )
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace context mismatch")
        
    require_feature(workspace, "mcp_access")

    async def event_generator():
        raw_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # 🎯 Clean the URL string to strip the problematic text query parameter
        if "?ssl_cert_reqs=CERT_NONE" in raw_redis_url:
            redis_url_str = raw_redis_url.split("?")[0]
        else:
            redis_url_str = raw_redis_url
            
        ssl_options = {}
        if redis_url_str.startswith("rediss://"):
            ssl_options["ssl_cert_reqs"] = ssl.CERT_NONE
            
        rc = redis.Redis.from_url(redis_url_str, decode_responses=True, **ssl_options)
        pubsub = rc.pubsub()
        pubsub.subscribe(f"stream:{step_id}")
        
        try:
            while True:
                # Read live messages pushing through the cross-platform Redis channel
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    token = message['data']
                    if token == "[DONE]":
                        break
                    yield token
                await asyncio.sleep(0.01)
        except Exception:
            pass
        finally:
            pubsub.unsubscribe(f"stream:{step_id}")

    return StreamingResponse(event_generator(), media_type="text/plain")