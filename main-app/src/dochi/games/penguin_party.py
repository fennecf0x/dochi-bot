from .game import MultiPlayerGame
import discord
import random
import os
from datetime import datetime
from typing import List, Optional, Tuple, Set, Union
from typing_extensions import Literal
from ..util import image


class PenguinParty(MultiPlayerGame):
    """
    0: no card
    1: red
    2: yellow
    3: green
    4: blue
    5: purple
    """

    COLORS = ["", "red", "yellow", "green", "blue", "purple"]

    def __init__(self, client: discord.Client, channel_id: int, player_id: int):
        super().__init__(client, channel_id, player_id, 6)
        self.prev_message: Optional[discord.Message] = None
        self.hand_messages: List[Optional[discord.Message]] = []
        self.board: List[int] = [0] * 36
        self.hands: List[List[int]] = [[None] * 5] * 6
        self.turn_index: int = 0
        self.surrendered_player_index: Set[int] = set()

    @staticmethod
    def index_to_pos(index: int) -> Tuple[int, int]:  # (level, offset)
        if index == -1:
            return (-1, 0)

        level = 0
        while index >= 36 - (7 - level) * (8 - level) / 2:
            level += 1

        offset = index - int(36 - (8 - level) * (9 - level) / 2)

        return (level, offset)

    @staticmethod
    def pos_to_index(pos: Tuple[int, int]) -> int:
        if pos[0] == -1:
            return -1

        return pos[1] + int(36 - (8 - pos[0]) * (9 - pos[0]) / 2)

    def available_poses(self) -> List[Tuple[int, int]]:
        result = []

        lowest = [index for index in range(0, 8) if self.board[index] > 0]

        if lowest == []:
            return [(0, 0)]
        elif max(lowest) < 7:
            result = [(-1, 0), (0, max(lowest) + 1)]

        for index in range(8, 36):
            level, offset = PenguinParty.index_to_pos(index)
            if (
                self.board[index] == 0
                and self.board[PenguinParty.pos_to_index((level - 1, offset))] != 0
                and self.board[PenguinParty.pos_to_index((level - 1, offset + 1))] != 0
            ):
                result.append((level, offset))

        result.sort(key=lambda x: (x[1], x[0]))

        return result

    def available_moves(self, player_index=None):
        if player_index is None:
            player_index = self.turn_index

        poses = self.available_poses()
        colors = set(self.hands[player_index])
        print("colors", list(colors))

        result = []

        for (i, (level, offset)) in enumerate(poses):
            if level <= 0:
                result.extend([(color, i) for color in colors])

            else:
                result.extend(
                    [
                        (color, i)
                        for color in colors
                        if color
                        in [
                            self.board[PenguinParty.pos_to_index((level - 1, offset))],
                            self.board[
                                PenguinParty.pos_to_index((level - 1, offset + 1))
                            ],
                        ]
                    ]
                )

        print("available_moves > result", result)
        return result

    def on_start(self):
        self.prev_message: Optional[discord.Message] = None
        self.hand_messages: List[Optional[discord.Message]] = []
        self.board: List[int] = [0] * 36

        random.seed(datetime.now())
        random.shuffle(self.player_ids)

        deck = [1, 2, 3, 4, 5] * 7 + [4]
        random.shuffle(deck)

        if len(self.player_ids) == 5:
            self.board[0] = deck.pop()

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i : i + n]

        self.hands = list(chunks(deck, 36 // len(self.player_ids)))
        for hand in self.hands:
            hand.sort()

        self.hand_messages = [None] * len(self.player_ids)
        self.prev_message = None
        self.turn_index = 0
        self.surrendered_player_index = set()

    def get_scores(self):  # -> Optional[dict[int, int]]:
        if self.is_finished:
            return dict(
                [
                    (player_id, -len(self.hands[i]))
                    for (i, player_id) in enumerate(self.player_ids)
                ]
            )

        return None

    def play(
        self, player: int, move: Tuple[int, int]
    ) -> Union[Literal[False], Tuple[Literal[True], Set[int]]]:
        """Play a move. Returns if move is valid or not."""
        if self.is_finished:
            return False

        if self.turn_index != player:
            return False

        card_color, index = move

        if card_color not in self.hands[player]:
            return False

        moves = self.available_moves()
        if move not in moves:
            return False

        board_pos = self.available_poses()[index]
        board_index = PenguinParty.pos_to_index(board_pos)

        if board_index == -1:
            if all(self.board[i] != 0 for i in range(8)):
                return False

            self.hands[player].remove(card_color)
            self.board.insert(0, card_color)
            self.board.pop()

        else:
            if self.board[board_index] != 0:
                return False

            self.hands[player].remove(card_color)
            self.board[board_index] = card_color

        # Check for the termination condition

        # the set of surrendered just after this turn
        newly_surrendered = set()

        # the set of players that have no moves on current board
        has_no_moves = [
            self.available_moves(i) == [] for i in range(len(self.player_ids))
        ]
        print("has_no_moves", has_no_moves)

        # repeat the following:
        while True:
            # change the turn
            self.turn_index += 1
            self.turn_index %= len(self.player_ids)

            print(self.turn_index)

            # if everyone is surrendered, terminate
            if len(self.surrendered_player_index) == len(self.player_ids):
                self.terminate()
                break

            # if self.turn_index has surrendered already, continue
            if self.turn_index in self.surrendered_player_index:
                continue

            # if the player has a move, break without termination
            if not has_no_moves[self.turn_index]:
                break

            # self.turn_index has no moves available.
            newly_surrendered.add(self.turn_index)
            self.surrendered_player_index.add(self.turn_index)

        return (True, newly_surrendered)

    @staticmethod
    def insert_image(
        color: int, level: int, offset: int, max_level: int = 7, indent: bool = True
    ) -> str:
        return f"""
        <image
            x="{12 + (96 + 12) * ((level / 2 if indent else 0) + offset)}"
            y="{12 + (96 + 12) * (max_level - level)}"
            width="96" height="96"
            xlink:href="{image.png_to_base64(os.environ.get('ASSETS_PATH', '') + '/penguin_party/' + PenguinParty.COLORS[color] + '.png')}"
        />
        """

    def print_hand(self, index: int) -> str:
        hand = self.hands[index]

        return f"""
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="isolation:isolate" viewBox="0 0 {12 + (96 + 12) * ((len(hand) + 1) // 2)} {12 + (96 + 12) * 2}" width="{12 + (96 + 12) * ((len(hand) + 1) // 2)}px" height="{12 + (96 + 12) * 2}px">
            <g>
                {"".join(PenguinParty.insert_image(t, 1 if i % 2 == 0 else 0, i // 2, max_level=1, indent=False) for (i, t) in enumerate(hand))}
            </g>
        </svg>
        """

    def print_board(self) -> str:
        gen_path = (
            lambda level, offset, max_level: f"""
            <path d="M 6 0 L 90 0 C 93.311 0 96 2.689 96 6 L 96 90 C 96 93.311 93.311 96 90 96 L 6 96 C 2.689 96 0 93.311 0 90 L 0 6 C 0 2.689 2.689 0 6 0 Z" transform="matrix(1,0,0,1,{
                12 + (96 + 12) * (level / 2 + offset)
            },{
                12 + (96 + 12) * (max_level - level)
            })" style="stroke:none;fill:#EBEBEB;stroke-miterlimit:10;" />
            """
        )
        gen_text = (
            lambda i, level, offset, max_level: f"""
            <text xmlns="http://www.w3.org/2000/svg" style='font-family:Noto Sans CJK KR;font-weight:600;font-size:36px;font-style:normal;fill:#373737;stroke:none;' dominant-baseline="middle" text-anchor="middle" transform="matrix(1,0,0,1,{
                12 + (96 + 12) * (level / 2 + offset) + 48
            },{
                12 + (96 + 12) * (max_level - level) + 60
            })">{i + 1}</text>
            """
        )

        available_poses = self.available_poses()
        max_level = max(
            [0]
            + [
                PenguinParty.index_to_pos(index)[0]
                for index in range(36)
                if self.board[index] != 0
            ]
            + [level for (level, _) in available_poses]
        )
        offset_offset = 1 if (-1, 0) in available_poses else 0
        width_list = [offset for (level, offset) in available_poses if level == 0]
        if width_list == []:
            width = 8
        else:
            width = max(width_list) + 1

        return f"""
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="isolation:isolate" viewBox="{-(96 + 12) * offset_offset} 0 {12 + (96 + 12) * (width + offset_offset)} {12 + (96 + 12) * (max_level + 1)}" width="{12 + (96 + 12) * (width + offset_offset)}px" height="{12 + (96 + 12) * (max_level + 1)}px">
        <g>
        {"".join(
            gen_path(level, offset, max_level) if level != -1 else gen_path(0, -1, max_level) for (level, offset) in self.available_poses()
        )}
        {"".join(
            gen_text(i, level, offset, max_level) if level != -1 else gen_text(i, 0, -1, max_level) for (i, (level, offset)) in enumerate(self.available_poses())
        )}
        {"".join(
            PenguinParty.insert_image(self.board[index], level, offset, max_level)
            for (index, (level, offset)) 
            in enumerate([PenguinParty.index_to_pos(index) for index in range(36)])
            if self.board[index] != 0
        )}
        </g>
        </svg>
        """
