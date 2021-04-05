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
        user_id: int,
        **kwargs,
    ):
        """
        return the invitation link.
        """

        if self.mute:
            state.muted.add(user_id)

        else:
            state.muted.remove(user_id)
