"""
schedule.py

Manage the APScheduler and define schedules
"""

from datetime import datetime, timedelta
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.combining import OrTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import random
import time
import math
from dochi.database import get, model, update

from ..state import state
from ..finance.coin_price import update_coin_params

scheduler = AsyncIOScheduler()


def add_job(func, *, weeks=0, days=0, hours=0, minutes=0, seconds=0, now=True, **kwargs):
    job = scheduler.add_job(
        func,
        **kwargs,
        trigger=OrTrigger(
            [
                *([DateTrigger(run_date=datetime.now())] if now else []),
                IntervalTrigger(
                    weeks=weeks,
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                ),
            ]
        ),
    )


def change_mood():
    five_days_in_seconds = 5 * 24 * 60 * 60

    mood = math.sin(2 * math.pi / five_days_in_seconds * time.time()) + random.uniform(
        -0.25, 0.25
    )
    mood = max(-1, min(mood, 1))

    state.mood = mood

    print("mood changed")


def decrease_likability():
    for user in list(model.User.select()):
        likability = get.likability_from_user(user)
        after_decrement = lambda v, r: max(
            0, v - r * 1.1 * (0.25 + v / 200 if v < 70 else 0.2 + 2.5 / (v - 60))
        )

        update.likability(
            user.user_id,
            kindliness=after_decrement(likability.kindliness, 0.7),
            unkindliness=after_decrement(likability.unkindliness, 1),
            friendliness=after_decrement(likability.friendliness, 0.7),
            unfriendliness=after_decrement(likability.unfriendliness, 1),
            respectfulness=after_decrement(likability.respectfulness, 0.7),
            disrespectfulness=after_decrement(likability.disrespectfulness, 1),
        )

    print("likability decreased")


def update_coin_price_database():
    for currency_type in state.coin_params:
        update_coin_params(currency_type, state.coin_params[currency_type])
        print(state.coin_params[currency_type])
