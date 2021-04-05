import os
import random
import discord
from ...state import state
from .item import CommandItem


class Mute(CommandItem):
    def __init__(self, mute: bool):
        self.mute = mute

    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        userid: int,
        **kwargs,
    ):
        """
        return the invitation link.
        """

        if self.mute:
            state.muted.add(userid)

        else:
            state.muted.remove(userid)
