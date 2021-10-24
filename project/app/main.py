import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.api import ping
from app.db import init_db
from app.managers.connection_manager import ConnectionManager
from app.managers.game_manager import GameManager, Move

connection_manager = ConnectionManager()
game_manager = GameManager(connection_manager)

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


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
