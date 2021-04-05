from .game import Game
import discord


class YootNori(Game):
    def __init__(self, client: discord.Client, channel_id: int):
        self.started = False

    pass
