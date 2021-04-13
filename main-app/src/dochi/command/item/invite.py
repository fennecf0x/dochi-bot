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

        guild_id_list = [
            int(guild_id)
            for guild_id in os.environ.get("GUILD_ID_LIST", "").split(",")
        ]
        if guild_id_list == []:
            return {**kwargs, "is_satisfied": False}

        channel = client.get_guild(guild_id_list[0]).text_channels[0]
        link = await channel.create_invite(max_age = 300)

        return {**kwargs, "link": link}
