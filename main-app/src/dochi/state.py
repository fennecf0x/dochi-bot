"""
State manager

Manage bot's states and global variables
"""

from dataclasses import dataclass
from typing import Set, cast
from dochi.util.dict import DictX


@dataclass
class State:
    mood: float
    root: str
    muted: Set[int]


state: State = cast(State, DictX({
    "mood": 0.0,
    "root": "/",
    "muted": set(),
}))
