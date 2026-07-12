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
import asyncio
import redis
import ssl
from fastapi import APIRouter, Header, HTTPException
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


@router.get("/stream/{step_id}")
async def mcp_stream_tokens(step_id: str, x_api_key: str = Header(None)):
    """
    Subscribes to the live task Redis channel, broadcasting tokens
    straight down an EventPipe stream while bypassing reverse-proxy cache layers.
    """
    raw_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    if "?ssl_cert_reqs=CERT_NONE" in raw_redis_url:
        redis_url_str = raw_redis_url.split("?")[0]
    else:
        redis_url_str = raw_redis_url
        
    ssl_options = {}
    if redis_url_str.startswith("rediss://"):
        ssl_options["ssl_cert_reqs"] = ssl.CERT_NONE

    redis_client = redis.Redis.from_url(redis_url_str, decode_responses=True, **ssl_options)
    pubsub_instance = redis_client.pubsub()
    pubsub_instance.subscribe(f"stream:{step_id}")

    async def event_generator():
        try:
            while True:
                # Poll the Redis pub/sub framework for incoming message frames
                message_node = pubsub_instance.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message_node and message_node.get("type") == "message":
                    token_payload = message_node.get("data", "")
                    
                    if token_payload == "[DONE]":
                        break
                        
                    # ⚡ Standard Server-Sent Events structure formatting string sequence
                    yield f"data: {token_payload}\n\n"
                    
                await asyncio.sleep(0.01)
        finally:
            pubsub_instance.unsubscribe(f"stream:{step_id}")
            pubsub_instance.close()

    # 🎯 CRITICAL HEADERS: Blocks corporate load balancers from buffering response content sets
    anti_buffering_headers = {
        "X-Accel-Buffering": "no",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive"
    }

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream", 
        headers=anti_buffering_headers
    )