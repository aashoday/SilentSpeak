from typing import List  # noqa: UP035

from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    """Manages active WebSocket connections to handle client lifecycle events gracefully."""

    def __init__(self):
        # Keeps track of all currently connected client WebSockets
        self.active_connections: List[WebSocket] = []  # noqa: UP006

    async def connect(self, websocket: WebSocket):
        """Accepts a new connection request and adds it to the tracking pool."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(
            f"⚡ [WS Manager] Client connected. Total active: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """Removes a disconnected client from the active pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(
                f"❌ [WS Manager] Client disconnected. Total active: {len(self.active_connections)}"
            )

    async def send_json(self, message: dict, websocket: WebSocket):
        """Sends a JSON response payload to a specific client safely."""
        try:
            # Check if the websocket is still open before sending
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            # Swallow exceptions if the socket closed mid-flight
            print(f"⚠️ [WS Manager] In-flight message skipped (socket closed): {e}")
            self.disconnect(websocket)


# Instantiate a singleton instance to use across your API routes
manager = ConnectionManager()
