import os
import re
import math
from datetime import datetime, timedelta

import discord
import tossi
import numpy as np
from apscheduler.triggers.interval import IntervalTrigger

from .schedule import schedule
from .state import state, State
from .database import get, currency_type_ko, CurrencyType
from .command import *


class DochiBot(discord.Client):
    def __init__(self, **options):
        intents = discord.Intents.all()
        super().__init__(**options, intents=intents)

        is_in_container = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)

        # initialize acceptable commands
        random_selection_commands = CommandGroup(
            Command(
                VsSelection(),
                SampleFrom(),
                MapArgs({"sample": "content"}),
                Send(),
            )
        )

        # TODO
        likability_update_commands = CommandGroup()

        bori_command = Command(
            ExactString("보리"),
            Filter(lambda c, m, k: "BORI_PATH" in os.environ),
            Args(path=os.environ["BORI_PATH"], absolute=True),
            ListFiles(),
            MapArgs({"files": "choices"}, is_random=True),
            SampleFrom(),
            MapArgs({"sample": "url"}, content=""),
            Send(),
        )

        analyze_emotion_items = lambda starts_with_dochi: [
            Args(starts_with_dochi=starts_with_dochi),
            AnalyzeEmotion(),
        ]
        emotion_commands = CommandGroup(
            Command(StartsWithDochi(), *analyze_emotion_items(True)),
            Command(Negation(StartsWithDochi()), *analyze_emotion_items(False)),
            Command(
                StartsWithDochi(),
                ExactString("호감도"),
                SerializeLikability(),
                MapArgs({"likability": "content"}),
                Send(),
            ),
        )

        test_commands = CommandGroup()

        self.group: CommandGroup = CommandGroup(
            random_selection_commands,
            likability_update_commands,
            bori_command,
            emotion_commands,
            CommandGroup() if is_in_container else test_commands,
        )

    async def on_ready(self):
        # add jobs to the scheduler
        schedule.add_job(schedule.change_mood, args=[self], hours=1)
        schedule.add_job(
            schedule.decrease_likability, args=[self], minutes=30, now=False
        )

        await self.change_presence(status=discord.Status.offline)
        print("Logged on as", self.user)

    async def on_message(self, message: discord.Message):
        # do not respond to messages of the bot itself
        if message.author == self.user:
            return

        # allow only selected guilds
        if message.guild is None or (
            message.guild.id
            not in [
                int(guild_id)
                for guild_id in os.environ.get("GUILD_ID_LIST", []).split(",")
            ]
        ):
            return

        # accept messages
        await self.group(self, message)
