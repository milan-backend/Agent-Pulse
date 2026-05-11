from fastapi import APIRouter, Depends
from app.api.deps import get_current_agent
from app.models.agent import Agent

from fastapi import Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.routes.steps import execute_step
from fastapi import BackgroundTasks

router = APIRouter()


@router.get("/tools")
def list_tools(current_agent: Agent = Depends(get_current_agent)):
    return {
        "tools": [
            {
                "name": "execute_task",
                "description": "Execute a durable task with reliability",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_name": {"type": "string"},
                        "input_data": {"type": "object"}
                    },
                    "required": ["task_name"]
                }
            },
            {
                "name": "get_step_status",
                "description": "Check status of a step",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "step_id": {"type": "string"}
                    },
                    "required": ["step_id"]
                }
            }
        ]
    }

@router.post("/execute")
def mcp_execute(
    body: dict = Body(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    tool = body.get("tool")
    args = body.get("arguments", {})

    if tool == "execute_task":
        return execute_step(
            request=args,
            background_tasks=background_tasks,
            db=db,
            current_agent=current_agent
        )

    return {"error": "Unknown tool"}