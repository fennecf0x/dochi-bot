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
from dochi.command.patterns import digits_of_pi, 줘, 봐, 뭐, 뭘


class DochiBot(discord.Client):
    def __init__(self, **options):
        intents = discord.Intents.all()
        super().__init__(**options, intents=intents)

        is_in_container = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)

        # initialize acceptable commands
        invitation_command = CommandGroup(
            Command(
                StartsWithDochi(),
                MatchRegex(f"초대해{줘}"),
                Invite(),
                MapArgs({"link": "content"}),
                Send(),
            )
        )

        random_selection_commands = CommandGroup(
            Command(
                VsSelection(),
                SampleFrom(),
                MapArgs({"sample": "content"}),
                Send(),
            )
        )

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

        pi_command = Command(
            StartsWithDochi(),
            MatchRegex(digits_of_pi, 4, 10, 12),
            MapArgs(
                lambda c, m, k: {
                    "base": 16
                    if k["groups"][0] is not None or k["groups"][1] is not None
                    else 10,
                    "n": int(k["groups"][2]),
                }
            ),
            GetNthDigitOfPi(),
            MapArgs({"digit": "content"}),
            Send(),
        )

        show_likability_command = Command(
            StartsWithDochi(),
            ExactString("호감도"),
            Args(ignore_likability_update=True),
            SerializeLikability(),
            MapArgs({"likability": "content"}),
            Send(),
        )

        send_list_command = Command(
            StartsWithDochi(),
            MatchRegex(r"\s*(.*?)\s*목록$", 1),
            MapArgs({"groups": "content"}),
            StripWhitespaces(),
            MapArgs({"content": "query"}),
            SendList(),
        )

        search_image_command = Command(
            StartsWithDochi(),
            MatchRegex(
                rf"(.*?)(\s*(검색(해\s*{줘}?{봐}?)|찾아{봐}?{줘}?{봐}?)|(이|가|은|는)?\s*({뭐}야|{뭘}까)\?*)$",
                1,
            ),
            MapArgs({"groups": "query"}),
            SearchImage(),
            Send(),
        )

        ff_lottery_commands = CommandGroup(
            Command(
                StartsWithDochi(),
                ExactString("복권"),
                StartFFLottery(),
                NotifyFFLottery(),
                Send(),
                DeleteFFLotteryMessage(),
                StoreFFLotteryMessage(),
            ),
            Command(
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                OneOf(MatchRegex(r"^복권\s+(.*?)$", 1), Filter(lambda c, m, k: True)),
                MapArgs(
                    lambda l, m, k: {
                        "content": k["groups" if "groups" in k else "content"].lower()
                    }
                ),
                MatchRegex(r"^[a-i]$"),
                MapArgs({"content": "move"}),
                PlayFFLottery(),
                NotifyFFLottery(),
                DeleteMessage(),
                Send(),
                DeleteFFLotteryMessage(),
                StoreFFLotteryMessage(),
            ),
        )

        # ff_tt_commands = CommandGroup(
        #     Command(
        #         StartsWithDochi(),
        #         OneOf(
        #             MatchRegex(r"^(파판|ff|FF|파이널판타지)?\s*트리플\s*트라이어드\s*(시작|참가|참여|할래|ㄱㄱ?)?$"),
        #             MatchRegex(r"^(파판|ff|FF|파이널판타지)?\s*카드\s*게임\s*(시작|참가|참여|할래|ㄱㄱ?)?$"),
        #         ),
        #         JoinFFTripleTriad(),
        #         NotifyFFTripleTriad(),
        #         Args(reply=True),
        #         Send(),
        #     ),
        # )

        analyze_emotion_items = lambda starts_with_dochi: [
            Args(starts_with_dochi=starts_with_dochi),
            AnalyzeEmotion(),
        ]
        self.likability_update_commands = CommandGroup(
            Command(StartsWithDochi(), *analyze_emotion_items(True)),
            Command(Negation(StartsWithDochi()), *analyze_emotion_items(False)),
        )

        self.mute_commands = CommandGroup(
            Command(
                IsAdmin(),
                MatchRegex(r"^\/mute\s+<@!(\d+?)>$", 1),
                MapArgs(lambda c, m, k: {"user_id": int(k["groups"])}),
                Mute(True),
            ),
            Command(
                IsAdmin(),
                MatchRegex(r"^\/unmute\s+<@!(\d+?)>$", 1),
                MapArgs(lambda c, m, k: {"user_id": int(k["groups"])}),
                Mute(False),
            ),
        )

        dotnick_command = Command(
            IsAdmin(),
            MatchRegex(r"^\/dotnick\s*(.*?)$", 1),
            MapArgs(lambda c, m, k: {"nickname": k["groups"]}),
            ChangeNickname(),
        )

        finance_commands = CommandGroup(
            Command(
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                StripWhitespaces(),
                IsCheckingWallet(),
                CheckWallet(),
                Send(),
            ),
            Command(
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                ExactString("돈줘"),
                ChangeFinance(
                    currency_type=CurrencyType.MONEY, amount=100, incremental=True
                ),
                Args(content="그랭"),
                Send(),
            ),
        )

        test_commands = CommandGroup(
            finance_commands,
            Command(
                ExactString("svg"),
                Args(svg="hihi"),
                Send(),
            ),
            Command(
                StartsWithDochi(),
                MatchRegex(rf"(.*?)\s*읽어{줘}", 1),
                MapArgs({"groups": "content"}),
                Shout(),
            ),
        )

        self.group: CommandGroup = CommandGroup(
            invitation_command,
            random_selection_commands,
            bori_command,
            show_likability_command,
            send_list_command,
            pi_command,
            search_image_command,
            dotnick_command,
            ff_lottery_commands,
            test_commands,
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

        await self.mute_commands(self, message)

        try:
            if message.author.id in state.muted:
                await message.delete()
                return

        except Exception as e:
            print("Exception during deleting message:", e)

        finally:
            # accept messages
            ignore_likability_update = await self.group(self, message)
            if not ignore_likability_update:
                await self.likability_update_commands(self, message)
