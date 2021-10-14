import os

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from tortoise.contrib.fastapi import register_tortoise

from app.config import Settings, get_settings
from app.managers.connection_manager import ConnectionManager
from app.managers.game_manager import GameManager, Move

app = FastAPI()
connection_manager = ConnectionManager()
game_manager = GameManager(connection_manager)

register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["app.models.tortoise"]},
    generate_schemas=False,
    add_exception_handlers=True,
)


@app.websocket("/{game_id}")
async def single_game(websocket: WebSocket, game_id: int):
    await connection_manager.connect(game_id, websocket)
    if connection_manager.connection_count(game_id) < 2:
        await connection_manager.send_personal_message(
            "Waiting for an opponent", websocket
        )
    elif connection_manager.connection_count(game_id) == 2:
        await connection_manager.broadcast(
            game_id, "Opponent found. Choose rock, paper, or scissors."
        )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                move = Move(data)
                await connection_manager.send_personal_message(
                    f"You played {move}", websocket
                )
                await game_manager.move(game_id, websocket, move=data)
            except ValueError:
                await connection_manager.send_personal_message(
                    f"Invalid move: {data}", websocket
                )
    except WebSocketDisconnect:
        connection_manager.disconnect(game_id, websocket)
        await connection_manager.broadcast(game_id, "Opponent has left the game")


@app.get("/test")
async def passing_test():
    """
    A temporary route just to have a passing test until I figure out how to
    test WebSockets
    """
    return {"msg": "Hello"}


@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
