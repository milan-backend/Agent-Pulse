import asyncio
import json

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from sqlalchemy.orm import Session

from app.db.session import SessionLocal

from app.models.workspace import Workspace

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.services.feature_access import (
    require_feature
)

from app.services.websocket_manager import (
    manager
)

router = APIRouter()


# ============================================
# BROADCAST MESSAGE
# ============================================

async def broadcast_message(
    data: dict
):
    await manager.broadcast(
        data
    )


# ============================================
# WEBSOCKET ENDPOINT
# ============================================

@router.websocket("/ws/live")
async def websocket_endpoint(
    websocket: WebSocket
):

    workspace_id = (
        websocket.query_params.get(
            "workspace_id"
        )
    )

    if not workspace_id:

        await websocket.close(
            code=4000
        )

        return

    db: Session = SessionLocal()

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if not workspace:

        await websocket.close(
            code=4004
        )

        return

    # ============================================
    # LOAD ACTIVE SUBSCRIPTION
    # ============================================

    subscription = (
        db.query(WorkspaceSubscription)
        .filter(
            WorkspaceSubscription.workspace_id
            == workspace.id,

            WorkspaceSubscription.status
            == "active"
        )
        .first()
    )

    workspace.subscription = subscription

    # ============================================
    # FEATURE ACCESS CHECK
    # ============================================

    try:

        require_feature(
            workspace,
            "live_websocket_updates"
        )

    except Exception:

        await websocket.close(
            code=4003
        )

        return

    await manager.connect(
        websocket
    )

    print(
        "WebSocket Connected"
    )

    try:

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

        print(
            "WebSocket Disconnected"
        )

        manager.disconnect(
            websocket
        )

    finally:

        db.close()