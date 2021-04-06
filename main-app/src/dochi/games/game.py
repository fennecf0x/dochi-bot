import discord
from typing import Any
from abc import ABC, abstractmethod


class Game(ABC):
    def is_multiplayer(self) -> bool:
        return self.id[0]

    @property
    def is_finished(self) -> bool:
        """Returns if the game is ended."""
        raise NotImplementedError

    @abstractmethod
    def play(self, player: int, move: Any) -> bool:
        """Play a move. Returns if move is valid or not."""
        raise NotImplementedError


class MultiPlayerGame(Game):
    def __init__(self, client: discord.Client, channel_id: int, player_id: int, max_num_players: int):
        assert max_num_players >= 2
        self.player_ids = [player_id]
        self.max_num_players = max_num_players
        self.id = (True, channel_id)
        self.is_playing = False

    def join(self, player_id: int) -> bool:
        if player_id in self.player_ids:
            return False

        if len(self.player_ids) >= self.max_num_players:
            return False

        self.player_ids.append(player_id)
        return True

    def start(self) -> bool:
        if self.is_playing:
            return False

        self.is_playing = True
        self.on_start()
        return True

    def on_start(self):
        """on starting game"""
        pass

    def leave(self, player_id: int) -> bool:
        if player_id in self.player_ids:
            self.player_ids.remove(player_id)
            return True

        return False

    def terminate(self) -> bool:
        if self.is_playing:
            self.is_playing = False
            return True

        return False

    @property
    def is_finished(self) -> bool:
        # when it is finished, it should be removed
        return not self.is_playing


class SinglePlayerGame(Game):
    def __init__(self, client: discord.Client, user_id: int):
        self.id = (False, self.__class__.__name__, user_id)

    def is_finished(self) -> bool:
        # when it is finished, it should be removed
        return False

