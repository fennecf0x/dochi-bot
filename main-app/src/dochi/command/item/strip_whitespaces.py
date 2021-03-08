from typing import Callable, Union
import discord
from .map_args import MapArgs
import dochi.util as util


class StripWhitespaces(MapArgs):
    def __init__(self):
        super().__init__(
            lambda client, message, kwargs: {
                **kwargs,
                **{"content": util.string.strip_whitespaces(kwargs["content"])},
            }
        )
