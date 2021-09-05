from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


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

    async def broadcast(self, game_id: int, message: str, skip: Optional[WebSocket]):
        for connection in self.active_connections[game_id]:
            if connection != skip:
                await connection.send_text(message)

    def connection_count(self, game_id: int):
        return len(self.active_connections[game_id])


manager = ConnectionManager()


class GameManager:
    def __init__(self):
        self.games: Dict[int, List[Tuple[WebSocket, str]]] = {}

    async def move(self, game_id: int, player: WebSocket, move: str):
        if game_id not in self.games:
            self.games[game_id] = []
        self.games[game_id].append((player, move))
        if len(self.games[game_id]) == 2:
            await self.resolve_game(game_id)

    async def resolve_game(self, game_id: int):
        for (player, move) in self.games[game_id]:
            message = f"Opponent played {move}"
            await manager.broadcast(game_id, message, skip=player)

        # TODO: declare winner

        self.games.pop(game_id)


game_manager = GameManager()


@app.websocket("/{game_id}")
async def single_game(websocket: WebSocket, game_id: int):
    await manager.connect(game_id, websocket)
    if manager.connection_count(game_id) < 2:
        await manager.send_personal_message("Waiting for an opponent", websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You played {data}", websocket)
            await game_manager.move(game_id, websocket, move=data)
    except WebSocketDisconnect:
        manager.disconnect(game_id, websocket)
        await manager.broadcast(game_id, f"Opponent has left the game")


@app.get("/test")
async def passing_test():
    """
    A temporary route just to have a passing test until I figure out how to
    test WebSockets
    """
    return {"msg": "Hello"}
