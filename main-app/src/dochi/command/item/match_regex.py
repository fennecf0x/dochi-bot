from typing import TypedDict
import re
import discord
from .item import CommandItem


class MatchRegex(CommandItem):
    def __init__(self, pattern: str, *group_indices: int):
        self.pattern = pattern
        self.group_indices = group_indices

    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        match = re.match(self.pattern, content)

        if match is None:
            return {**kwargs, "is_satisfied": False}

        if len(self.group_indices) == 0:
            return {**kwargs, "is_satisfied": True}

        try:
            return {
                **kwargs,
                "is_satisfied": True,
                "groups": match.group(*self.group_indices),
            }

        except IndexError:
            return {**kwargs, "is_satisfied": True}
