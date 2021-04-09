import discord
from .item import CommandItem
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import aiohttp
from io import BytesIO
import os
import ujson
from dochi.state import state
import math
import random
import time
from dochi.database import get, update, Likability
import numpy as np


class SerializeLikability(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        user_id = str(message.author.id)
        likability = get.likability(user_id)
        serialized_likability = (
            f"친절: {likability.kindliness - likability.unkindliness:.2f}\n"
            f"친밀: {likability.friendliness - likability.unfriendliness:.2f}\n"
            f"존경: {likability.respectfulness - likability.disrespectfulness:.2f}\n"
        )

        return {**kwargs, "content": serialized_likability}
