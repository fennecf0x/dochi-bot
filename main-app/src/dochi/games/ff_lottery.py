from .game import SinglePlayerGame
import discord
import random
from typing import List, Literal, Optional


class FFLottery(SinglePlayerGame):
    def __init__(self, client: discord.Client, user_id: int):
        super().__init__(client, user_id)

        self.board: List[int] = list(range(1, 10))
        self.revealed: List[bool] = [True] + [False] * 8
        self.selected_line: Optional[
            Literal["a", "b", "c", "d", "e", "f", "g", "h"]
        ] = None
        random.shuffle(self.board)
        random.shuffle(self.revealed)

        self.stage: int = 0  # select spot at 0, 1, 2
        # select line at 3, show result at 4

        self.prev_message: Optional[discord.Message] = None

    def play(
        self, player: int, move: Literal["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    ) -> bool:
        """Play a move. Returns if move is valid or not."""
        if self.stage < 3:
            validity = not self.revealed[ord(move) - 97]

            if not validity:
                return False

            self.stage += 1
            self.revealed[ord(move) - 97] = True

            return True

        if self.stage == 3:
            validity = move != "i"

            if not validity:
                return False

            self.stage += 1
            self.selected_line = move

            for index in self.get_indices():
                self.revealed[index] = True

            return True

    def get_indices(self) -> List[int]:
        if self.selected_line == "a":
            indices = [6, 7, 8]
        elif self.selected_line == "b":
            indices = [3, 4, 5]
        elif self.selected_line == "c":
            indices = [0, 1, 2]
        elif self.selected_line == "d":
            indices = [0, 4, 8]
        elif self.selected_line == "e":
            indices = [0, 3, 6]
        elif self.selected_line == "f":
            indices = [1, 4, 7]
        elif self.selected_line == "g":
            indices = [2, 5, 8]
        elif self.selected_line == "h":
            indices = [2, 4, 6]

        return indices

    def get_points(self) -> Optional[int]:
        if self.selected_line is None:
            return None

        indices = self.get_indices()

        s = sum(self.board[i] for i in indices)

        points = [
            10000,
            36,
            720,
            360,
            80,
            252,
            108,
            72,
            54,
            180,
            72,
            180,
            119,
            36,
            306,
            1080,
            144,
            1800,
            3600,
        ]

        return points[s - 6]

    @staticmethod
    def num_to_emoji(num: int) -> str:
        return f":{['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][num - 1]}:"

    def num_to_emoji_hidden(self, index: int, hidden_char: Optional[str] = None) -> str:
        return (
            FFLottery.num_to_emoji(self.board[index])
            if self.revealed[index]
            else f":regional_indicator_{chr(97 + index)}:"
            if hidden_char is None
            else hidden_char
        )

    def line_to_emoji_hidden(self, char: int) -> str:
        if char != self.selected_line:
            return ":black_small_square:"

        if char in "abc":
            return ":arrow_right:"

        if char in "d":
            return ":arrow_lower_right:"

        if char in "efg":
            return ":arrow_down:"

        if char in "h":
            return ":arrow_lower_left:"

    def print_board(self) -> str:
        if self.stage < 3:
            return "\n".join(
                [
                    " ".join([":black_small_square:"] * 7),
                    " ".join([":black_small_square:"] * 7),
                    *[
                        " ".join(
                            [
                                ":black_small_square: :black_small_square:",
                                *[
                                    self.num_to_emoji_hidden(3 * row + col)
                                    for col in range(3)
                                ],
                                ":black_small_square: :black_small_square:",
                            ]
                        )
                        for row in range(3)
                    ],
                    " ".join([":black_small_square:"] * 7),
                    " ".join([":black_small_square:"] * 7),
                ]
            )

        if self.stage == 3:
            return "\n".join(
                [
                    ":regional_indicator_d: :black_small_square: :regional_indicator_e: :regional_indicator_f: :regional_indicator_g: :black_small_square: :regional_indicator_h:",
                    ":black_small_square: :arrow_lower_right: :arrow_down: :arrow_down: :arrow_down: :arrow_lower_left: :black_small_square:",
                    *[
                        " ".join(
                            [
                                f":regional_indicator_{chr(99 - row)}: :arrow_right:",
                                *[self.num_to_emoji(3 * row + col) for col in range(3)],
                                ":black_small_square: :black_small_square:",
                            ]
                        )
                        for row in range(3)
                    ],
                    " ".join([":black_small_square:"] * 7),
                    " ".join([":black_small_square:"] * 7),
                ]
            )

        if self.stage == 4:
            return "\n".join(
                [
                    " ".join([":black_small_square:"] * 7),
                    f':black_small_square: {self.line_to_emoji_hidden("d")} {self.line_to_emoji_hidden("e")} {self.line_to_emoji_hidden("f")} {self.line_to_emoji_hidden("g")} {self.line_to_emoji_hidden("h")} :black_small_square:',
                    *[
                        " ".join(
                            [
                                f":black_small_square: {self.line_to_emoji_hidden(chr(99 - row))}",
                                *[
                                    self.num_to_emoji_hidden(
                                        3 * row + col, ":yellow_square:"
                                    )
                                    for col in range(3)
                                ],
                                ":black_small_square: :black_small_square:",
                            ]
                        )
                        for row in range(3)
                    ],
                    " ".join([":black_small_square:"] * 7),
                    " ".join([":black_small_square:"] * 7),
                ]
            )
