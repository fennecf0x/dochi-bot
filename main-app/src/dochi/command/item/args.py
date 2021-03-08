import discord
from .item import CommandItem


class Args(CommandItem):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        return {**kwargs, **self.kwargs}
