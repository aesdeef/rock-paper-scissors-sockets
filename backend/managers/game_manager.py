from enum import Enum
from typing import Dict, List, Tuple

from fastapi import WebSocket

from .connection_manager import ConnectionManager


class Move(str, Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class GameManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.games: Dict[int, List[Tuple[WebSocket, str]]] = {}

    async def move(self, game_id: int, player: WebSocket, move: Move):
        if game_id not in self.games:
            self.games[game_id] = []
        self.games[game_id].append((player, move))
        if len(self.games[game_id]) == 2:
            await self.resolve_game(game_id)

    async def resolve_game(self, game_id: int):
        for (player, move) in self.games[game_id]:
            message = f"Opponent played {move}"
            await self.connection_manager.broadcast(game_id, message, skip=player)

        # TODO: declare winner

        self.games.pop(game_id)
