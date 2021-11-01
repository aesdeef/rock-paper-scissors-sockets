from itertools import permutations

from app.errors import AlreadyPlayedError, MaxNumberOfPlayersReached
from app.move import Move
from app.outcome import get_outcome, outcome_message
from app.player import Player


class Game:
    def __init__(self):
        self.players: set[Player] = set()
        self.moves: dict[Player, Move] = {}

    def get_players(self) -> set[Player]:
        return self.players

    async def add_player(self, player: Player):
        if len(self.players) < 2:
            self.players.add(player)
        else:
            raise MaxNumberOfPlayersReached

        if self.player_count() < 2:
            await player.send("Waiting for an opponent")
        elif self.player_count() == 2:
            await self.broadcast("Opponent found. Choose rock, paper, or scissors.")

    def remove_player(self, player: Player):
        self.players.remove(player)

    async def broadcast(self, message: str):
        for player in self.players:
            await player.send(message)

    def player_count(self) -> int:
        return len(self.players)

    async def record_move(self, player: Player, move: Move):
        if player in self.moves:
            raise AlreadyPlayedError

        self.moves[player] = move

        if len(self.moves) == 2:
            await self.resolve_game()

    async def resolve_game(self):
        for player, opponent in permutations(self.players):
            players_move = self.moves[player]
            opponents_move = self.moves[opponent]
            outcome = get_outcome(players_move, opponents_move)

            await player.send(f"Opponent played {opponents_move}")
            await player.send(outcome_message[outcome])

        self.moves = {}
