from fastapi import WebSocket
import json


class ConnectionManager:

    def __init__(self):
        self.active_connections = set()

    async def connect(
        self,
        websocket: WebSocket
    ):
        await websocket.accept()

        self.active_connections.add(
            websocket
        )

    def disconnect(
        self,
        websocket: WebSocket
    ):
        if websocket in self.active_connections:
            self.active_connections.remove(
                websocket
            )

    async def broadcast(
        self,
        data: dict
    ):
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(
                    json.dumps(data)
                )

            except Exception:
                disconnected.append(
                    connection
                )

        for connection in disconnected:
            self.disconnect(
                connection
            )


manager = ConnectionManager()