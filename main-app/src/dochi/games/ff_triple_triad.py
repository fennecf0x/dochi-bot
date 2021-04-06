from .game import MultiPlayerGame
import discord
import random
from typing import List, Literal, Optional
from ..util import image


class FFTripleTriad(MultiPlayerGame):
    def __init__(self, client: discord.Client, channel_id: int, player_ids: List[int]):
        super().__init__(client, channel_id)

        self.player_ids = player_ids
        random.shuffle(self.player_ids)
        self.board: List[Optional[str]] = [None] * 9
        self.turn_index = 0

    def play(
        self, player: int, move: Literal["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    ) -> bool:
        """Play a move. Returns if move is valid or not."""

    @staticmethod
    def insert_pattern(basename: str, row: int, column: int) -> str:
        return f"""
        <pattern id="{basename}" x="{12 + 268 * column}" y="{12 + 268 * row}" patternUnits="userSpaceOnUse" height="256" width="256">
            <image x="0" y="0" xlink:href="{image.png_to_base64(os.environ['ASSETS_PATH'] + '/ff_tt/' + basename + '.png')}"></image>
        </pattern>
        """

    def print_board(self) -> str:
        gen_path = (
            lambda i: f"""
            <path d="M 28 12 L 252 12 C 260.831 12 268 19.169 268 28 L 268 252 C 268 260.831 260.831 268 252 268 L 28 268 C 19.169 268 12 260.831 12 252 L 12 28 C 12 19.169 19.169 12 28 12 Z" style="transform:translate({268 * (i % 3)}px,{268 * (i // 3)}px);stroke:none;fill:{'url(#' + self.board[i] + ')' if  self.board[i] is not None  else '#EBEBEB'};stroke-miterlimit:10;" />
            """
        )
        return f"""
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="isolation:isolate" viewBox="0 0 816 816" width="816px" height="816px">
            <defs>
                {"".join(
                   FFTripleTriad.insert_pattern(self.board[i], i // 3, i % 3) for i in range(9) if self.board[i] is not None
                )}
            </defs>
            <g>
                {"".join(gen_path(i) for i in range(9))}
            </g>
        </svg>
        """
