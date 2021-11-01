from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.errors import AlreadyPlayedError, MaxNumberOfPlayersReached
from app.game import Game
from app.move import Move
from app.player import Player

app = FastAPI()
game = Game()


@app.websocket("/")
async def single_game(websocket: WebSocket):
    await websocket.accept()
    player = Player(websocket)
    try:
        await game.add_player(player)
    except MaxNumberOfPlayersReached:
        await player.send("Sorry, we already have two players")
        await player.disconnect()
        return

    if game.player_count() < 2:
        await player.send("Waiting for an opponent")
    elif game.player_count() == 2:
        await game.broadcast("Opponent found. Choose rock, paper, or scissors.")

    try:
        while True:
            data = await player.receive()
            try:
                move = Move(data)
                await game.record_move(player, move)
                await player.send(f"You played {move}")
            except AlreadyPlayedError:
                await player.send("You have already played")
            except ValueError:
                await player.send(f"Invalid move: {data}")
    except WebSocketDisconnect:
        game.remove_player(player)
        await game.broadcast("Opponent has left the game")
