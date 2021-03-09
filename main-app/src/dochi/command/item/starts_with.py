from typing import TypedDict
import re
import discord
from .item import CommandItem


class StartsWith(CommandItem):
    def __init__(self, needle: str):
        self.needle = needle

    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        if content[:len(self.needle)] != self.needle:
            return {**kwargs, "is_satisfied": False}

        return {**kwargs, "is_satisfied": True}
