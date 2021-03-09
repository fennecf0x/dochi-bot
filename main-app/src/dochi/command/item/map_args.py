from typing import Callable, Union
import discord
from .item import CommandItem


class MapArgs(CommandItem):
    def __init__(self, mapping: Union[Callable, dict], **_kwargs):
        self.kwargs = _kwargs

        if type(mapping) == dict:
            self.mapping = lambda client, message, kwargs: {
                # old keys
                **dict(
                    (key, val)
                    for (key, val) in kwargs.items()
                    if key not in [mapping[k] for k in kwargs.keys() if k in mapping]  # type: ignore
                    and key not in mapping  # type: ignore
                ),
                # new keys
                **dict(
                    (mapping[key], val)  # type: ignore
                    for (key, val) in kwargs.items()
                    if key in mapping  # type: ignore
                ),
            }
        else:
            self.mapping = mapping  # type: ignore

    async def __call__(
        self, client: discord.Client, message: discord.Message, **kwargs
    ):
        return {**self.mapping(client, message, kwargs), **self.kwargs}
