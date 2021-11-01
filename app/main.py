from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.managers.connection_manager import ConnectionManager
from app.managers.game_manager import GameManager, Move

app = FastAPI()
connection_manager = ConnectionManager()
game_manager = GameManager(connection_manager)


@app.websocket("/")
async def single_game(websocket: WebSocket):
    await connection_manager.connect(websocket)
    if connection_manager.connection_count() < 2:
        await connection_manager.send_personal_message(
            "Waiting for an opponent", websocket
        )
    elif connection_manager.connection_count() == 2:
        await connection_manager.broadcast(
            "Opponent found. Choose rock, paper, or scissors."
        )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                move = Move(data)
                await connection_manager.send_personal_message(
                    f"You played {move}", websocket
                )
                await game_manager.move(websocket, move)
            except ValueError:
                await connection_manager.send_personal_message(
                    f"Invalid move: {data}", websocket
                )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast("Opponent has left the game")
