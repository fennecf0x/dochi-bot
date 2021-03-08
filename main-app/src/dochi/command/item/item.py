from typing import Optional, TypeVar, Generic, Any
import abc
import discord


class CommandItem:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        raise NotImplementedError
