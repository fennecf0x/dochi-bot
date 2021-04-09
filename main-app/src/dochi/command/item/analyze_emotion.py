from typing import Optional
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
from dochi.util.string import strip_whitespaces


saltlux_cache = dict()


class AnalyzeEmotion(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        starts_with_dochi: bool = False,
        **kwargs,
    ):
        endpoint = "http://svc.saltlux.ai:31781"
        service_id = "11987300804"

        stripped_content = strip_whitespaces(content)

        if stripped_content in saltlux_cache:
            emotion, reliability = saltlux_cache[stripped_content]
        
        else:
            if "SALTLUX_KEY" not in os.environ:
                return kwargs

            content = content.strip()
            if len(content) <= 2:
                return kwargs

            headers = {"content-type": "application/json"}

            payload = {
                "key": os.environ["SALTLUX_KEY"],
                "serviceId": service_id,
                "argument": {"type": "1", "query": content},
            }

            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.post(endpoint, json=payload) as resp:
                        text = await resp.text()
                        json_resp = ujson.loads(text)

                        emotion, reliability = (
                            json_resp["Result"][0][1],
                            json_resp["Result"][0][0],
                        )
                        saltlux_cache[stripped_content] = (emotion, reliability)

            except Exception as e:
                print("error", e)
                emotion, reliability = None, 0

        random.seed(time.time())
        base_score = lambda: (
            (
                state.mood
                + 2
                * math.sqrt((random.random() + 1) / 2)
                * min(1, 1.5 * reliability ** 1.3 + 0.5)
                + state.mood / 3
            )
            / 8
            * (4 if starts_with_dochi else 1)
            * (1.7 if len(content) > 10 else 1)
        )
        base = lambda v: max(base_score(), 0) / math.sqrt(0.0375 * v + 0.25) / 7

        multipliers = (0, 0, 0, 0, 0, 0)
        if emotion == "기쁨":
            multipliers = (1, 0, 2, 0, 0, 0)
        if emotion == "신뢰":
            multipliers = (1, 0, 0.3, 0, 1.7, 0)
        if emotion == "공포":
            multipliers = (0, 1, 1, 0, 0, 1)
        if emotion == "놀라움":
            multipliers = (0, 0, 2, 0, 1, 0)
        if emotion == "슬픔":
            multipliers = (1, 0, 0.7, 0, 0, 0.3)
        if emotion == "혐오":
            multipliers = (0, 0, 0, 1, 0, 1)
        if emotion == "분노":
            multipliers = (0, 1, 1, 0, 0, 1)
        if emotion == "기대":
            multipliers = (1.2, 0, 1.5, 0, 0, 0)

        noise = (np.random.dirichlet([2] * 6) + [0.01, -0.04] * 3) / 2

        user_id = str(message.author.id)

        likability = get.likability(user_id)

        update.likability(
            user_id,
            kindliness=likability.kindliness
            + base(likability.kindliness) * multipliers[0]
            + noise[0],
            unkindliness=likability.unkindliness
            + base(likability.unkindliness) * multipliers[1]
            + noise[1],
            friendliness=likability.friendliness
            + base(likability.friendliness) * multipliers[2]
            + noise[2],
            unfriendliness=likability.unfriendliness
            + base(likability.unfriendliness) * multipliers[3]
            + noise[3],
            respectfulness=likability.respectfulness
            + base(likability.respectfulness) * multipliers[4]
            + noise[4],
            disrespectfulness=likability.disrespectfulness
            + base(likability.disrespectfulness) * multipliers[5]
            + noise[5],
        )

        return kwargs
