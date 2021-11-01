from typing import Dict, List, Optional

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, game_id: int, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, game_id: int, websocket: WebSocket):
        self.active_connections[game_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(
        self, game_id: int, message: str, skip: Optional[WebSocket] = None
    ):
        for connection in self.active_connections[game_id]:
            if connection != skip:
                await connection.send_text(message)

    def connection_count(self, game_id: int) -> int:
        return len(self.active_connections[game_id])
