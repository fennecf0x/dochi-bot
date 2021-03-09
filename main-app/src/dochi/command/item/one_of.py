from typing import TypedDict, Optional
import discord
from .item import CommandItem
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import aiohttp
from io import BytesIO


class OneOf(CommandItem):
    def __init__(
        self, *command_items: CommandItem
    ):
        self.command_items = command_items

    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        for command_item in self.command_items:
            new_kwargs = await command_item(client, message, **kwargs)

            if "is_satisfied" in new_kwargs and new_kwargs["is_satisfied"]:
                return {**new_kwargs, "is_satisfied": True}

        return {**kwargs, "is_satisfied": False}

