from typing import List, Union, Optional
import discord
import asyncio

from .command import Command


flatten = lambda t: [item for sublist in t for item in sublist]


class CommandGroup:
    """
    A free monad representing a collection of commands
    """

    def __init__(self, *commands: Union["CommandGroup", Command]):
        self._commands = commands

    @property
    def commands(self):
        return flatten([[command] if type(command) == Command else command.commands for command in self._commands])
        
    async def __call__(self, client: discord.Client, message: discord.Message):
        ignore_likability_update_list = await asyncio.gather(*[command(client, message) for command in self.commands])
        return any(ignore_likability_update_list)
