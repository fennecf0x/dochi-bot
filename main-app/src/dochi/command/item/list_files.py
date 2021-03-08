import os
import random
import discord
from .item import CommandItem


class ListFiles(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        path: str,
        absolute: bool = False,
        **kwargs,
    ):
        """
        return the list of regular files inside the directory.
        """

        try:
            files = next(os.walk(path))[2]

            if absolute:
                files = [os.path.abspath(os.path.join(path, item)) for item in files]

            return {**kwargs, "files": files}

        except Exception as e:
            return {**kwargs, "files": []}
