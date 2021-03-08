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

from ..state import state

scheduler = AsyncIOScheduler()


def add_job(func, *, weeks=0, days=0, hours=0, minutes=0, seconds=0, **kwargs):
    job = scheduler.add_job(
        func,
        **kwargs,
        trigger=OrTrigger(
            [
                DateTrigger(run_date=datetime.now()),
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


def change_mood(client: discord.Client):
    five_days_in_seconds = 5 * 24 * 60 * 60

    mood = math.sin(2 * math.pi / five_days_in_seconds * time.time()) + random.uniform(
        -0.25, 0.25
    )
    mood = max(-1, min(mood, 1))

    state.mood = mood

    print("mood changed")
