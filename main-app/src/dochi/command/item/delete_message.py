import os
import random
import discord
from .item import CommandItem


class DeleteMessage(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        delete the message from the user
        """
        
        try:
            await message.delete()

        except:
            pass

        return kwargs
