from typing import Callable
import discord
from .item import CommandItem


class IsAdmin(CommandItem):
    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        if message.author.id == 455782902173532162:
            return {**kwargs, "is_satisfied": True}

        return {**kwargs, "is_satisfied": False}
