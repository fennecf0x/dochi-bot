from typing import TypedDict
import re
import discord
from .item import CommandItem


dochi_pattern = r"^(도\s*치\s*(봇\s*님?|야|님)?|돛\s*봇?\s*님?)\s*(.*?)$"


class StartsWithDochi(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        match = re.match(dochi_pattern, content)

        if match is None:
            return {**kwargs, "is_satisfied": False}

        return {**kwargs, "is_satisfied": True, "content": match.group(3)}
