"""
State manager

Manage bot's states and global variables
"""

from dataclasses import dataclass
from typing import cast
from dochi.util.dict import DictX


@dataclass
class State:
    mood: float
    root: str


state: State = cast(State, DictX({
    "mood": 0.0,
    "root": "/"
}))
