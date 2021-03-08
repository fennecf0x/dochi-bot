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
    def __init__(self):
        # initialize acceptable commands
        random_selection_commands = CommandGroup(
            Command(
                VsSelection(),
                SampleFrom(),
                MapArgs({"sample": "content"}),
                Send(),
            )
        )

        likability_update_commands = CommandGroup()
        
        bori_command = Command(
            ExactString("보리"),
            Args(path=os.environ["BORI_PATH"], absolute=True),
            ListFiles(),
            MapArgs({"files": "choices"}),
            SampleFrom(),
            MapArgs({"sample": "url"}),
            Send(),
        )

        self.group: CommandGroup = CommandGroup(
            random_selection_commands,
            likability_update_commands,
            bori_command,
        )


    async def on_ready(self):
        # add jobs to the scheduler
        schedule.add_job(schedule.change_mood, args=[self], hours=1)

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
                int(guild_id) for guild_id in os.environ["GUILD_ID_LIST"].split(",")
            ]
        ):
            return


        # accept messages
        await self.group(self, message)
