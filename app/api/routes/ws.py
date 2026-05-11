from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

import asyncio
import json

router = APIRouter()

connections = []


async def broadcast_message(data: dict):

    disconnected = []

    for connection in connections:

        try:

            await connection.send_text(
                json.dumps(data)
            )

        except:

            disconnected.append(connection)

    for connection in disconnected:

        if connection in connections:
            connections.remove(connection)


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    connections.append(websocket)

    print("WebSocket Connected")

    try:

        while True:

            # heartbeat every 2 seconds
            await websocket.send_text(
                json.dumps({
                    "type": "heartbeat",
                    "message": "connected"
                })
            )

            await asyncio.sleep(2)

    except WebSocketDisconnect:

        print("WebSocket Disconnected")

        if websocket in connections:
            connections.remove(websocket)