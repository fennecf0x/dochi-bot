from typing import List, TypedDict, TypeVar, Generic, Hashable
import random
import time
import math
import discord
from .item import CommandItem
from dochi.state import state

T = TypeVar("T", bound=Hashable)


class SampleFrom(CommandItem, Generic[T]):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        is_random: bool = False,
        choices: List[T],
        n: int = 1,
        **kwargs,
    ):
        """
        Choose a `sample` of size `min(n, len(choices))` from `choices: List[T]`
        according to the `value` determined from the seed.
        The seed is related to the `mood` of the bot
        """

        sample_size = min(n, len(choices))

        if is_random:
            random.seed(time.time())
            sample = random.sample(choices, k=sample_size)

            if sample_size == 1:
                return {**kwargs, "sample": sample[0]}

            return {**kwargs, "sample": sample}

        prioritised_choices = []

        for choice in choices:
            random.seed(hash(choice))
            seed = random.random()
            random.seed(seed + state.mood)
            priority = random.random()
            prioritised_choices.append((priority, choice))

        prioritised_choices.sort(key=lambda student: student[1])

        sample = [choice for (priority, choice) in prioritised_choices[:sample_size]]

        if sample_size == 1:
            return {**kwargs, "sample": sample[0]}

        return {**kwargs, "sample": sample}
