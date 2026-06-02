import asyncio
import json
from datetime import datetime
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

# Import system structural models
from app.models.workspace import Workspace
from app.models.workspace_subscription import WorkspaceSubscription

# Import core infrastructure service tools
from app.services.feature_access import require_feature
from app.services.websocket_manager import manager

# Import our secure ticket store container memory allocations
from app.services.user_auth_service import WEBSOCKET_TICKET_STORE

router = APIRouter()

# ============================================
# BROADCAST MESSAGE
# ============================================
async def broadcast_message(data: dict):
    await manager.broadcast(data)

# ============================================
# WEBSOCKET ENDPOINT (SECURED WITH SINGLE-USE TICKETS) 🛡️
# ============================================
@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Gather configuration connection parameter attributes
    workspace_id = websocket.query_params.get("workspace_id")
    ticket = websocket.query_params.get("ticket")

    # Access protection check: Ensure both query keys exist
    if not workspace_id or not ticket:
        await websocket.close(code=4000)  # Bad Request footprint mapping boundary
        return

    # 2. CRITICAL SECURITY STEP: POP AND VALIDATE THE TICKET 
    # Calling pop() reads the data and removes it instantly, making the ticket single-use!
    ticket_data = WEBSOCKET_TICKET_STORE.pop(ticket, None)

    if not ticket_data:
        print(f"WebSocket Connection Rejected: Ticket '{ticket}' is invalid or has already been used.")
        await websocket.close(code=4003)  # Forbidden access execution limits
        return

    if ticket_data["expires_at"] < datetime.utcnow():
        print(f"WebSocket Connection Rejected: Ticket '{ticket}' has expired.")
        await websocket.close(code=4003)  # Forbidden access execution limits
        return

    # 3. Establish Local Database Context
    db: Session = SessionLocal()

    try:
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )

        if not workspace:
            await websocket.close(code=4004)  # Workspace not found boundary
            return

        # ============================================
        # LOAD ACTIVE SUBSCRIPTION
        # ============================================
        subscription = (
            db.query(WorkspaceSubscription)
            .filter(
                WorkspaceSubscription.workspace_id == workspace.id,
                WorkspaceSubscription.status == "active"
            )
            .first()
        )

        workspace.subscription = subscription

        # ============================================
        # FEATURE ACCESS CHECK
        # ============================================
        try:
            require_feature(workspace, "live_websocket_updates")
        except Exception:
            await websocket.close(code=4003)  # Tier access tier restricted boundary
            return

        # 4. Hand over the secure connection straight to our centralized manager array
        await manager.connect(websocket)
        print(f"WebSocket Connected Securely for Workspace: {workspace_id}")

        # 5. Heartbeat loop processing block
        while True:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "heartbeat",
                        "message": "connected"
                    }
                )
            )
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print(f"WebSocket Disconnected for Workspace: {workspace_id}")
        manager.disconnect(websocket)

    finally:
        db.close()
