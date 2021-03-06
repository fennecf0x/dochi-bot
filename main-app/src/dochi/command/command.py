from typing import List, Union, Optional
from datetime import datetime
import discord

from .item import CommandItem


class Command:
    def __init__(self, *items: CommandItem):
        self.items = items

    async def __call__(self, client: discord.Client, message: discord.Message):
        kwargs: Optional[dict] = None
        content: str = message.content

        ignore_likability_update = False

        for item in self.items:
            try:
                kwargs = kwargs or {}

                if "content" not in kwargs:
                    kwargs["content"] = content
                else:
                    content = kwargs["content"]

                kwargs = await item(client, message, **kwargs)

                if kwargs is not None and "is_satisfied" in kwargs:
                    if not kwargs["is_satisfied"]:
                        return ignore_likability_update

                    kwargs.pop("is_satisfied", None)

                if kwargs is not None and "ignore_likability_update" in kwargs:
                    if kwargs["ignore_likability_update"]:
                        ignore_likability_update = True

                    kwargs.pop("ignore_likability_update", False)

            except Exception as e:
                raise e

        return ignore_likability_update
