import os
import re
import math
import time
import random
from datetime import datetime, timedelta
from threading import Thread

import discord
import tossi
import numpy as np
from apscheduler.triggers.interval import IntervalTrigger

from .schedule import schedule
from .state import state, State
from .database import get, currency_type_ko, CurrencyType
from .command import *
from dochi.command.patterns import digits_of_pi, 줘, 봐, 뭐, 뭘

from .finance.coin_price import update_price, initialize_coin_params


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
            Send(),
        )

        send_list_command = Command(
            StartsWithDochi(),
            MatchRegex(r"\s*(.*?)\s*목록$", 1),
            MapArgs({"groups": "content"}),
            StripWhitespaces(),
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
                OneOf(MatchRegex(r"^복권\s*(.*?)$", 1), Filter(lambda c, m, k: True)),
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

        ff_tt_commands = CommandGroup(
            Command(
                StartsWithDochi(),
                MatchRegex(
                    r"^(파판|ff|FF|파이널판타지)?\s*(트리플\s*트라이어드|트\.?트|카드\s*게임)\s*(시작|참가|참여|할래|ㄱㄱ?)?$"
                ),
                JoinFFTripleTriad(),
                NotifyFFTripleTriad(),
                Send(),
                StoreFFTripleTriadMessage(),
            ),
            Command(
                StartsWithDochi(),
                MatchRegex(
                    r"^(파판|ff|FF|파이널판타지)?\s*(트리플\s*트라이어드|트\.?트|카드\s*게임)\s*((종료|취소)(할래)?|(안|그만)\s*할래)$"
                ),
                TerminateFFTripleTriad(),
                Send(),
            ),
            Command(
                StartsWithDochi(),
                MatchRegex(
                    r"^(파판|ff|FF|파이널판타지)?\s*(트리플\s*트라이어드|트\.?트|카드\s*게임)\s*(옵션|설정)?\s*(.*?)$",
                    4,
                ),
                MapArgs({"groups": "content"}),
                StripWhitespaces(),
                ProcessOptionsFFTripleTriad(),
                Send(),
            ),
            Command(
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                OneOf(
                    MatchRegex(
                        r"^(파판|ff|FF|파이널판타지)?\s*(트리플\s*트라이어드|트\.?트|카드\s*게임)\s*(.*?)$", 3
                    ),
                    Filter(lambda c, m, k: True),
                ),
                MapArgs(
                    lambda l, m, k: {
                        "content": k["groups" if "groups" in k else "content"].lower()
                    }
                ),
                MatchRegex(
                    r"^([1-5])?[\s,\.]*([a-i])$|^([a-i])[\s,\.]*([1-5])?$", 1, 2, 3, 4
                ),
                MapArgs(
                    lambda c, m, k: {
                        "move": (
                            int(k["groups"][0] or k["groups"][3])
                            if (k["groups"][0] or k["groups"][3]) is not None
                            else None,
                            k["groups"][1] or k["groups"][2],
                        )
                    }
                ),
                PlayFFTripleTriad(),
                NotifyFFTripleTriad(),
                DeleteMessage(),
                Send(),
                DeleteFFTripleTriadMessage(),
                StoreFFTripleTriadMessage(),
            ),
        )

        penguin_party_commands = CommandGroup(
            Command(
                StartsWithDochi(),
                MatchRegex(r"^(펭귄\s*파티|펭귄\s*게임|펭귄\s*겜|펭파|펭귄)\s*(참가|참여|할래|시작|ㄱㄱ?)?$"),
                StartPenguinParty(),
                NotifyPenguinParty(),
                JoinPenguinParty(),
                Send(),
                StorePenguinPartyMessage(),
            ),
            Command(
                StartsWithDochi(),
                MatchRegex(r"^(펭귄\s*파티|펭귄\s*게임|펭귄\s*겜|펭파|펭귄)\s*(나갈래|퇴장|(안|그만)\s*할래)$"),
                ExitPenguinParty(),
                Send(),
            ),
            Command(
                StartsWithDochi(),
                MatchRegex(
                    r"^(펭귄\s*파티|펭귄\s*게임|펭귄\s*겜|펭파|펭귄)\s*((종료|취소)(할래)?)$"
                ),
                TerminatePenguinParty(),
                Send(),
            ),
            Command(
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                OneOf(
                    MatchRegex(r"^(펭귄\s*파티|펭귄\s*게임|펭귄\s*겜|펭파|펭귄)\s*(.*?)$", 2),
                    Filter(lambda c, m, k: True),
                ),
                MapArgs(
                    lambda l, m, k: {
                        "content": k["groups" if "groups" in k else "content"].lower()
                    }
                ),
                MatchRegex(
                    r"^((r|빨강?)|(y|노랑?)|(g|초록?)|(b|파랑?)|(p|보라?))[\s,\.]*([1-8])$|^([1-8])[\s,\.]*((r|빨강?)|(y|노랑?)|(g|초록?)|(b|파랑?)|(p|보라?))$",
                    2,  # 0: r
                    3,  # 1: y
                    4,  # 2: g
                    5,  # 3: b
                    6,  # 4: p
                    7,  # 5: num
                    8,  # 6: num
                    10,  # 7: r
                    11,  # 8: y
                    12,  # 9: g
                    13,  # 10: b
                    14,  # 11: p
                ),
                MapArgs(
                    lambda c, m, k: {
                        "move": (
                            1
                            if k["groups"][0] or k["groups"][7] is not None
                            else 2
                            if k["groups"][1] or k["groups"][8] is not None
                            else 3
                            if k["groups"][2] or k["groups"][9] is not None
                            else 4
                            if k["groups"][3] or k["groups"][10] is not None
                            else 5,
                            int(k["groups"][5] or k["groups"][6]) - 1,
                        )
                    }
                ),
                PlayPenguinParty(),
                NotifyPenguinParty(),
                DeleteMessage(),
                Send(),
                DeletePenguinPartyMessage(),
                StorePenguinPartyMessage(),
            ),
        )

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

        mynick_command = Command(
            IsAdmin(),
            MatchRegex(r"^\/mynick\s*(.*?)$", 1),
            MapArgs(lambda c, m, k: {"nickname": k["groups"]}),
            ChangeMyNickname(),
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
                    currency_type=CurrencyType.MONEY, amount=random.randint(1, 1000), incremental=True
                ),
                Args(content="그랭"),
                Send(),
            ),
            Command(
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                StripWhitespaces(),
                MatchRegex(r"<@!(\d+)>에게(\d+)원기부", 1, 2),
                MapArgs(lambda c, m, k: {
                    "amount": float(k["groups"][1]),
                    "user_id": int(k["groups"][0]),
                }),
                DonateMoney(),
                Send(),
            ),
            Command(
                IsAdmin(),
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                StripWhitespaces(),
                MatchRegex(r"<@!(\d+)>에게서(\d+)원몰수", 1, 2),
                MapArgs(lambda c, m, k: {
                    "amount": -float(k["groups"][1]),
                    "user_id": int(k["groups"][0]),
                }),
                ChangeFinance(
                    currency_type=CurrencyType.MONEY, incremental=True
                ),
                Args(content="몰수햇어"),
                Send(),
            ),
            Command(
                IsAdmin(),
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                StripWhitespaces(),
                ExactString("돈많이줘"),
                ChangeFinance(
                    currency_type=CurrencyType.MONEY, amount=30000, incremental=True
                ),
                Args(content="그랭"),
                Send(),
            ),
            Command(
                IsAdmin(),
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                StripWhitespaces(),
                ExactString("돈짱많이줘"),
                ChangeFinance(
                    currency_type=CurrencyType.MONEY, amount=10000000, incremental=True
                ),
                Args(content="그랭"),
                Send(),
            ),
            Command(
                Negation(IsAdmin()),
                OneOf(StartsWithDochi(), Filter(lambda c, m, k: True)),
                StripWhitespaces(),
                ExactString("돈많이줘"),
                ChangeFinance(
                    currency_type=CurrencyType.MONEY, amount=-100, incremental=True
                ),
                Args(content="ㅅㄹ 뺏어갈거임"),
                Send(),
            ),
            Command(
                StartsWithDochi(),
                StripWhitespaces(),
                IsTransacting(),
                TransactCurrency(),
                Send(),
            ),
            Command(
                StartsWithDochi(),
                StripWhitespaces(),
                IsCheckingCurrencyPrice(),
                CheckCurrencyPrice(),
                Send(),
            ),
        )

        shout_command = Command(
            StartsWithDochi(),
            MatchRegex(rf"(.*?)\s*읽어{줘}", 1),
            MapArgs({"groups": "content"}),
            Shout(),
        )

        test_commands = CommandGroup(
            Command(
                StartsWithDochi(),
                ExactString("버전"),
                Args(content=os.environ.get("COMMIT", "UNKNOWN")),
                Send(),
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
            mynick_command,
            shout_command,
            finance_commands,
            ff_lottery_commands,
            ff_tt_commands,
            penguin_party_commands,
            test_commands,
        )

    async def on_ready(self):
        # add jobs to the scheduler
        schedule.add_job(schedule.change_mood, args=[], hours=1)
        schedule.add_job(schedule.decrease_likability, args=[], minutes=30, now=False)
        schedule.add_job(
            schedule.update_coin_price_database, args=[], seconds=10, now=False
        )
        schedule.add_job(
            update.drop_old_currency_price_records, args=[1], hours=6, now=False
        )

        coin_threads: dict = {}
        MAX_COIN_PRICES_LEN = 10000

        def run_update_price_thread(currency_type):
            while True:
                try:
                    update_price(
                        state.coin_constants[currency_type],
                        state.coin_params[currency_type],
                    )
                    update.currency_price_record(
                        currency_type,
                        timestamp=time.time(),
                        price=state.coin_params[currency_type].price,
                    )
                except Exception as e:
                    print("run_update_price_thread gave an error", e)

        # add coin price updater
        for currency_type in state.coin_constants:
            state.coin_params[currency_type] = initialize_coin_params(
                currency_type, state.coin_constants[currency_type]
            )
            thread = Thread(target=run_update_price_thread, args=(currency_type,))
            thread.setDaemon(True)
            thread.start()
            coin_threads[currency_type] = thread

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
                for guild_id in os.environ.get("GUILD_ID_LIST", "").split(",")
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

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        try:
            if after.id == int(os.environ.get("ADMIN_ID", 0)) and after.nick != state.my_nick:
                await after.edit(nick=state.my_nick)
        except:
            pass
