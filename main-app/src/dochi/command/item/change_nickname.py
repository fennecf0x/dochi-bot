import os
import random
import discord
from ...state import state
from .item import CommandItem


class ChangeNickname(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        nickname: str,
        **kwargs,
    ):
        """
        change the nickname
        """

        await message.guild.me.edit(username=nickname)
