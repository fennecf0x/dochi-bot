import os
import random
import discord
from .item import CommandItem
from ...state import state


class DeleteMessageFuture(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        prev_message: discord.Message,
        **kwargs,
    ):
        state.messages_to_delete[message.author.id] = state.messages_to_delete.get(
            message.author.id, []
        ) + [prev_message]

        return {**kwargs, "prev_message": prev_message}
