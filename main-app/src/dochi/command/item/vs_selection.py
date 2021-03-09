from typing import List, TypedDict
import re
import discord
from .item import CommandItem
from .send import Send
import dochi.util as util


class VsSelection(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        if not re.search(r"vs", content):
            return {**kwargs, "is_satisfied": False}

        content = content.strip()
        vs_front = False
        vs_back = False
        if content.startswith("vs"):
            vs_front = True
        if content.endswith("vs"):
            vs_back = True

        choices = re.split(r"vs(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", content)
        choices = [item for item in choices if item != ""]
        
        if vs_front:
            choices[0] = "vs" + choices[0]
        
        if vs_back:
            choices[-1] = choices[-1] + "vs"
        
        choices = [item.strip() for item in choices]

        if len(choices) <= 1:
            return {**kwargs, "is_satisfied": False}

        d = {util.string.strip_whitespaces(x): x for x in choices}
        choices = list(d.values())

        if len(choices) == 1:
            # it is certainly a `vs selection` but there is only one choice
            content = "ㅋㅋ"
            await Send()(client, message, content=content)

            return {**kwargs, "is_satisfied": False}

        return {**kwargs, "is_satisfied": True, "choices": choices}
