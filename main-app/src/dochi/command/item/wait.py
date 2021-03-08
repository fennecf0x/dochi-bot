import asyncio
import discord
from .item import CommandItem


class Wait(CommandItem):
    def __init__(self, seconds: float):
        self.seconds = seconds

    async def __call__(
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        await asyncio.sleep(self.seconds)
        return kwargs
