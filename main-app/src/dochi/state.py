"""
State manager

Manage bot's states and global variables
"""

from dataclasses import dataclass
from typing import Tuple, Set, cast
from dochi.util.dict import DictX
from dochi.games.game import Game


@dataclass
class State:
    mood: float
    root: str
    muted: Set[int]
    games: dict[Tuple[bool, str, int], Game]


state: State = cast(State, DictX({
    "mood": 0.0,
    "root": "/",
    "muted": set(),
    "games": {},
}))
