"""
State manager

Manage bot's states and global variables
"""

from dataclasses import dataclass
from typing import List, Tuple, Set, cast
from dochi.util.dict import DictX
from dochi.games.game import Game
from dochi.database.types import CurrencyType


coin_constants = {
    CurrencyType.DOCHI_COIN: DictX({
        "BASE_PRICE": 36523,
        "TIME_SLICE_LOW": 6,
        "TIME_SLICE_HIGH": 10,
        "TIMER_INC_DEC_FACTOR": 6.8,
        "TIMER_DEC_DEC_FACTOR": 2.8,
        "TIMER_INC_LOW": 6000,
        "TIMER_INC_HIGH": 40000,
        "TIMER_DEC_LOW": 8000,
        "TIMER_DEC_HIGH": 36000,
        "TIMER_INC_THRES_LOW": 1000,
        "TIMER_INC_THRES_HIGH": 3000,
        "TIMER_DEC_THRES_LOW": 500,
        "TIMER_DEC_THRES_HIGH": 6000,
        "PRICE_BIG_NOISE_FACTOR": 0.4,
        "PRICE_SMALL_NOISE_FACTOR": 0.025,
        "EWMA_HIGH_THRES_LOW": 1.375,
        "EWMA_HIGH_THRES_HIGH": 1.7,
        "EWMA_LOW_THRES_LOW": 0.74,
        "EWMA_LOW_THRES_HIGH": 0.85,
        "ALPHA1": 0.00011,
        "ALPHA2": 0.00002,
        # to show figure
        "COLORS": ["#4899E7", "#9C7EC4"],
    }),
    CurrencyType.AYACHISAAYA: DictX({
        "BASE_PRICE": 2872,
        "TIME_SLICE_LOW": 9,
        "TIME_SLICE_HIGH": 15,
        "TIMER_INC_DEC_FACTOR": 10.2,
        "TIMER_DEC_DEC_FACTOR": 3.5,
        "TIMER_INC_LOW": 6000,
        "TIMER_INC_HIGH": 40000,
        "TIMER_DEC_LOW": 8000,
        "TIMER_DEC_HIGH": 36000,
        "TIMER_INC_THRES_LOW": 1000,
        "TIMER_INC_THRES_HIGH": 3000,
        "TIMER_DEC_THRES_LOW": 500,
        "TIMER_DEC_THRES_HIGH": 4000,
        "PRICE_BIG_NOISE_FACTOR": 0.4,
        "PRICE_SMALL_NOISE_FACTOR": 0.025,
        "EWMA_HIGH_THRES_LOW": 1.375,
        "EWMA_HIGH_THRES_HIGH": 1.5,
        "EWMA_LOW_THRES_LOW": 0.74,
        "EWMA_LOW_THRES_HIGH": 0.89,
        "ALPHA1": 0.00009,
        "ALPHA2": 0.000018,

        "COLORS": ["#E895A9", "#EBD4BB"],
    }),
    CurrencyType.ROOT_COIN: DictX({
        "BASE_PRICE": 14812,
        "TIME_SLICE_LOW": 8,
        "TIME_SLICE_HIGH": 20,
        "TIMER_INC_DEC_FACTOR": 4.2,
        "TIMER_DEC_DEC_FACTOR": 4.5,
        "TIMER_INC_LOW": 6000,
        "TIMER_INC_HIGH": 28000,
        "TIMER_DEC_LOW": 8000,
        "TIMER_DEC_HIGH": 36000,
        "TIMER_INC_THRES_LOW": 2500,
        "TIMER_INC_THRES_HIGH": 4000,
        "TIMER_DEC_THRES_LOW": 1000,
        "TIMER_DEC_THRES_HIGH": 4000,
        "PRICE_BIG_NOISE_FACTOR": 0.3,
        "PRICE_SMALL_NOISE_FACTOR": 0.015,
        "EWMA_HIGH_THRES_LOW": 1.375,
        "EWMA_HIGH_THRES_HIGH": 1.8,
        "EWMA_LOW_THRES_LOW": 0.84,
        "EWMA_LOW_THRES_HIGH": 0.92,
        "ALPHA1": 0.00021,
        "ALPHA2": 0.00004,

        "COLORS": ["#F6BF6F", "#FEC926"],
    })
}

@dataclass
class State:
    mood: float
    root: str
    muted: Set[int]
    games: dict # dict[Game.id, Game]
    coin_constants: dict  # dict[CurrencyType, CoinPriceConstants]
    coin_params: dict  # dict[CurrencyType, CoinPriceParams]
    nicks: dict # dict[int, str]
    messages_to_delete: dict # dict[int (author id), List[discord.Message]]


state: State = cast(State, DictX({
    "mood": 0.0,
    "root": "/",
    "muted": set(),
    "games": {},
    "coin_constants": coin_constants,
    "coin_params": DictX({}),
    "nicks": {
        int(os.environ.get("ADMIN_ID")): "카누"
    },
    "messages_to_delete": {},
}))
