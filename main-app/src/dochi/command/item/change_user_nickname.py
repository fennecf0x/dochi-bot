import os
import random
import discord
from ...state import state
from .item import CommandItem


class ChangeUserNickname(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        user_id: int,
        nickname: str,
        **kwargs,
    ):
        """
        change the nickname
        """

        state.nicks[user_id] = nickname

        me = message.guild.get_member(user_id)
        await me.edit(nick=nickname)
