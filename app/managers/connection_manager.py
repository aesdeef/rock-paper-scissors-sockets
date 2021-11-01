from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    def get_players(self) -> set[WebSocket]:
        return self.active_connections

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        if self.connection_count() < 2:
            self.active_connections.add(websocket)
        else:
            await self.send_personal_message(
                "Sorry, we already have two players", websocket
            )
            await websocket.close()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    def connection_count(self) -> int:
        return len(self.active_connections)
