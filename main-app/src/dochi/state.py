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
        "TIMER_INC_DEC_FACTOR": 3.4,
        "TIMER_DEC_DEC_FACTOR": 2.8,
        "TIMER_INC_LOW": 6000,
        "TIMER_INC_HIGH": 40000,
        "TIMER_DEC_LOW": 8000,
        "TIMER_DEC_HIGH": 36000,
        "TIMER_INC_THRES_LOW": 1000,
        "TIMER_INC_THRES_HIGH": 3000,
        "TIMER_DEC_THRES_LOW": 500,
        "TIMER_DEC_THRES_HIGH": 6000,
        "PRICE_BIG_NOISE_FACTOR": 0.15,
        "PRICE_SMALL_NOISE_FACTOR": 0.005,
        "EWMA_HIGH_THRES_LOW": 1.375,
        "EWMA_HIGH_THRES_HIGH": 1.7,
        "EWMA_LOW_THRES_LOW": 0.74,
        "EWMA_LOW_THRES_HIGH": 0.85,
        "ALPHA1": 0.00011,
        "ALPHA2": 0.00002,
    })
}

@dataclass
class State:
    mood: float
    root: str
    muted: Set[int]
    games: dict #[Tuple[bool, str, int], Game]
    coin_constants: dict  # dict[CurrencyType, CoinPriceConstants]
    coin_params: dict  # dict[CurrencyType, CoinPriceParams]


state: State = cast(State, DictX({
    "mood": 0.0,
    "root": "/",
    "muted": set(),
    "games": {},
    "coin_constants": coin_constants,
    "coin_params": DictX({}),
}))
