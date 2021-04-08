import discord
import hashlib
import random
import numpy as np
import asyncio
import math
from .item import CommandItem
from ...state import state


class SendList(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        if content == "":
            return kwargs

        guild: Optional[discord.Guild] = message.guild
        if guild is None:
            return
        
        m = hashlib.sha256()
        m.update(content.encode())
        content_hash = m.digest().hex() + str(state.mood)

        random.seed(content_hash)

        members = [member async for member in guild.fetch_members(limit=None)]
        names = set(
            [member.nick for member in members if member.nick is not None]
            + [member.name for member in members]
        )
        sample = []
        if content in names:
            sample = [member for member in members if member.nick == content or member.name == content]
            random.seed(content_hash)
            random.shuffle(sample)
            n = len(sample)

        if sample == []:
            random.seed(content_hash)
            np.random.seed(hash(content_hash) % 2 ** 32)
            n = 1 + max(1, min(8, math.floor(np.random.gamma(shape=2.5))))
            sample = random.sample(members, n)

        for i in range(n):
            await message.channel.send(
                str(i + 1)
                + ". "
                + (
                    f"{sample[i].nick} ({sample[i].name})"
                    if sample[i].nick is not None and sample[i].nick != sample[i].name
                    else sample[i].name
                )
            )
            await asyncio.sleep(0.5)

        return kwargs
