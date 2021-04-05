from typing import Tuple, Literal, List, Optional
from .game import Game


Player = Tuple[Literal["Member", "CPU"], int]
GameType = Literal["YootNori"]


class Room:
    def __init__(self, channel_id: int, game_type: GameType, player_id: int):
        self.channel_id: int = channel_id
        self.game_type: GameType = game_type
        self.game: Optional[Game] = None
        self.player_id_list: List[Player] = [("Member", player_id)]

    def join(self, player_id: int) -> bool:
        if ("Member", player_id) in self.player_id_list:
            return False

        self.player_id_list.append(("Member", player_id))

    def start_game(self) -> bool:
        if self.game is not None:
            return False
        
        self.game = ...

        return True
