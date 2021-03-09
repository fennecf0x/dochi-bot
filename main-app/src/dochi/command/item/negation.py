from typing import TypedDict, Optional
import discord
from .item import CommandItem
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import aiohttp
from io import BytesIO


class Negation(CommandItem):
    def __init__(
        self, command_item: CommandItem
    ):
        self.command_item = command_item

    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        kwargs = await self.command_item(client, message, **kwargs)

        if "is_satisfied" in kwargs and kwargs["is_satisfied"]:
            return {**kwargs, "is_satisfied": False}

        return {**kwargs, "is_satisfied": True}

