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
        query: str,
        **kwargs,
    ):
        if query == "":
            return kwargs

        guild: Optional[discord.Guild] = message.guild
        if guild is None:
            return

        members = [member async for member in guild.fetch_members(limit=None)]
        names = set(
            [member.nick for member in members if member.nick is not None]
            + [member.name for member in members]
        )
        sample = []
        if query in names:
            sample = [member for member in members if member.nick == query or member.name == query]
            n = len(sample)

        if sample == []:
            m = hashlib.sha256()
            m.update(query.encode())
            query_hash = m.digest().hex() + str(state.mood)

            random.seed(query_hash)
            np.random.seed(hash(query_hash) % 2 ** 32)
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
