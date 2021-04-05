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
    def __init__(self, client: discord.Client, channel_id: int):
        self.id = (True, self.__class__.__name__, channel_id)


class SinglePlayerGame(Game):
    def __init__(self, client: discord.Client, user_id: int):
        self.id = (False, self.__class__.__name__, user_id)

