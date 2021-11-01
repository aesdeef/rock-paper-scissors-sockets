from enum import Enum, auto
from typing import Dict, List, Tuple

from fastapi import WebSocket

from app.managers.connection_manager import ConnectionManager


class Move(str, Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class Outcome(Enum):
    LOSS = auto()
    DRAW = auto()
    WIN = auto()


outcome_message = {
    Outcome.LOSS: "You lost!",
    Outcome.DRAW: "It's a draw!",
    Outcome.WIN: "You won!",
}


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
        outcome = self.get_outcome(game_id)
        for (player, opponents_move, result) in outcome:
            await self.connection_manager.send_personal_message(
                f"Opponent played {opponents_move}", player
            )
            await self.connection_manager.send_personal_message(
                outcome_message[result], player
            )
        self.games.pop(game_id)

    def get_outcome(self, game_id: int):
        players, moves = zip(*self.games[game_id])

        if moves[0] == moves[1]:
            outcomes = (Outcome.DRAW, Outcome.DRAW)
        elif tuple(moves) in {
            (Move.ROCK, Move.SCISSORS),
            (Move.PAPER, Move.ROCK),
            (Move.SCISSORS, Move.PAPER),
        }:
            outcomes = (Outcome.WIN, Outcome.LOSS)
        else:
            outcomes = (Outcome.LOSS, Outcome.WIN)

        return zip(players, moves[::-1], outcomes)
