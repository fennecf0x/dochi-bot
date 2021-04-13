import os
import random
import discord
from ...state import state
from .item import CommandItem


class ChangeMyNickname(CommandItem):
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

        state.my_nick = nickname

        # TODO: hardcoded id
        me = message.guild.get_member(455782902173532162)
        await me.edit(nick=nickname)
