from enum import Enum, auto

from app.move import Move


class Outcome(Enum):
    LOSS = auto()
    DRAW = auto()
    WIN = auto()


outcome_message = {
    Outcome.LOSS: "You lost!",
    Outcome.DRAW: "It's a draw!",
    Outcome.WIN: "You won!",
}


def get_outcome(players_move: Move, opponents_move: Move) -> Outcome:
    if players_move == opponents_move:
        return Outcome.DRAW

    if (players_move, opponents_move) in {
        (Move.ROCK, Move.SCISSORS),
        (Move.PAPER, Move.ROCK),
        (Move.SCISSORS, Move.PAPER),
    }:
        return Outcome.WIN

    return Outcome.LOSS
