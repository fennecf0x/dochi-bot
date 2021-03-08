from typing import Callable
import discord
from .item import CommandItem


class Filter(CommandItem):
    def __init__(
        self, predicate: Callable[[discord.Client, discord.Message, dict], bool]
    ):
        # predicate: (client, message, kwargs) -> bool
        #                              ^ note there is no `**` operator here
        self.predicate = predicate

    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        if self.predicate(client, message, kwargs):
            return {**kwargs, "is_satisfied": True}

        return {"is_satisfied": False}
