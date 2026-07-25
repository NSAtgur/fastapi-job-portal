from fastapi import WebSocket
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # One user can have multiple active WebSocket connections
        # (multiple tabs, devices, etc.)
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

        logger.info("User %s connected. Active connections: %d",
                    user_id,
                    len(self.active_connections[user_id]))

    def disconnect(self, user_id: int, websocket: WebSocket):
        connections = self.active_connections.get(user_id)

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            self.active_connections.pop(user_id, None)

        logger.info("User %s disconnected", user_id)

    async def send_to_user(self, user_id: int, message: str):
        connections = self.active_connections.get(user_id)

        if not connections:
            logger.info("User %s is offline", user_id)
            return

        disconnected = set()

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        # Clean up dead connections
        for websocket in disconnected:
            connections.discard(websocket)

        if not connections:
            self.active_connections.pop(user_id, None)


manager = ConnectionManager()