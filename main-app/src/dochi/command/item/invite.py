import os
import random
import discord
from .item import CommandItem


class Invite(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        return the invitation link.
        """

        MAIN_GUILD_ID = int(os.environ.get("MAIN_GUILD_ID", "0"))
        if MAIN_GUILD_ID == 0:
            return {**kwargs, "is_satisfied": False}

        channel = client.get_guild(MAIN_GUILD_ID).text_channels[0]
        link = await channel.create_invite(max_age = 300)

        return {**kwargs, "link": link}
