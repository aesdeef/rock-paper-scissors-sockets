from enum import Enum, auto

from fastapi import WebSocket

from app.errors import AlreadyPlayedError
from app.managers.connection_manager import ConnectionManager


class Move(str, Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

    @staticmethod
    def compare_moves(players_move: "Move", opponents_move: "Move"):
        if players_move == opponents_move:
            return Outcome.DRAW

        if (players_move, opponents_move) in {
            (Move.ROCK, Move.SCISSORS),
            (Move.PAPER, Move.ROCK),
            (Move.SCISSORS, Move.PAPER),
        }:
            return Outcome.WIN

        return Outcome.LOSS


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
        self.game: dict[WebSocket, Move] = {}

    async def move(self, player: WebSocket, move: Move):
        if player in self.game:
            raise AlreadyPlayedError()

        self.game[player] = move
        if len(self.game) == 2:
            await self.resolve_game()

    async def resolve_game(self):
        players = tuple(self.connection_manager.get_players())

        for player, opponent in (players, players[::-1]):
            players_move = self.game[player]
            opponents_move = self.game[opponent]
            result = Move.compare_moves(players_move, opponents_move)

            await self.connection_manager.send_personal_message(
                f"Opponent played {opponents_move}", player
            )
            await self.connection_manager.send_personal_message(
                outcome_message[result], player
            )

        self.game = {}
