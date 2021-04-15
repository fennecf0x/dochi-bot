from .game import MultiPlayerGame
import discord
import random
import os
from datetime import datetime
from typing import List, Optional, Tuple
from ..util import image


class FFTripleTriad(MultiPlayerGame):
    CARDS = {  # (right, up, left, down)
        "wai_cinnamoroll": (4, 3, 5, 2),
        "standing_yoshi": (7, 1, 1, 4),
        "standing_kirby": (1, 6, 5, 1),
        "skateboard_cinnamoroll": (1, 2, 3, 7),
        "rubberduck_chiffon": (5, 2, 3, 5),
        "orange_mushroom": (2, 5, 1, 5),
        "lovely_daengdaeng": (2, 2, 6, 4),
        "lovely_bt": (1, 6, 4, 3),
        "lamb_cinnamoroll": (3, 5, 3, 3),
        "greeting_pikachu": (7, 3, 1, 2),
        "full_kuromi": (4, 2, 5, 3),
        "foxy_redfox": (1, 2, 6, 5),
        "delusion_rabbit": (5, 5, 2, 2),
        "crying_mocha": (2, 1, 4, 6),
        "bitter_mymelody": (4, 3, 3, 4),
        "birthday_redfox": (1, 4, 7, 1),
    }

    def __init__(self, client: discord.Client, channel_id: int, player_id: int):
        super().__init__(client, channel_id, player_id, 2)
        self.prev_message: Optional[discord.Message] = None
        self.hands = [[None] * 5, [None] * 5]
        self.hand_messages: List[Optional[discord.Message]] = [None, None]
        self.board: List[Optional[Tuple[str, int]]] = [None] * 9
        self.options = {
            "동수": False,
            "합산": False,
            "순서대로": False,
            "랜덤순서": False,
            "랜덤": False,
        }
        self.turn_index = 0

    @staticmethod
    def tile_to_str(tile: Tuple[str, int]):
        """
        tile = ("card_name", player_index)
        """
        return f"{tile[0]}_{('blue' if tile[1] % 2 == 0 else 'red')}"

    def on_start(self):
        self.board: List[Optional[Tuple[str, int]]] = [None] * 9
        self.turn_index = 0

        cards = FFTripleTriad.CARDS.keys()

        random.seed(datetime.now())
        random.shuffle(self.player_ids)

        # TODO: currently hands are determined randomly
        self.hands = [random.sample(cards, 5), random.sample(cards, 5)]
        if self.options["랜덤순서"]:
            random.shuffle(self.hands)

        if self.options["랜덤"]:
            self.options["동수"] = random.choice([True, False])
            self.options["합산"] = random.choice([True, False])
            self.options["순서대로"], self.options["랜덤순서"] = random.choice(
                [
                    (False, False),
                    (False, False),
                    (False, True),
                    (True, False),
                ]
            )

        self.hand_messages = [None, None]
        self.prev_message = None

    def get_winner(self) -> Optional[int]:  # -1: draw
        if self.is_finished:
            num_tile = len([tile for tile in self.board if tile[1] == 0])
            return 0 if num_tile > 5 else 1 if num_tile < 5 else -1

        return None

    def play(self, player: int, move: Tuple[int, str]) -> bool:
        """Play a move. Returns if move is valid or not."""
        if self.is_finished:
            return False

        if self.turn_index != player:
            return False

        if self.options["순서대로"] or self.options["랜덤순서"]:
            move = (
                6 - len([hand for hand in self.hands[player] if hand is None]),
                move[1],
            )

        card_name = self.hands[player][move[0] - 1]
        if card_name is None:
            return False

        board_index = ord(move[1]) - 97
        if self.board[board_index] is not None:
            return False

        self.hands[player][move[0] - 1] = None

        changed_card_positions = [board_index]

        self.board[board_index] = (card_name, player)

        # check for "SAME"
        if self.options["동수"]:
            affected_cards = self.check_same(board_index)
            if len(affected_cards) >= 2:
                changed_card_positions.extend(
                    [pos for pos in affected_cards if self.board[pos][1] != player]
                )

        # check for "PLUS"
        if self.options["합산"]:
            affected_cards = self.check_plus(board_index)
            changed_card_positions.extend(
                [pos for pos in affected_cards if self.board[pos][1] != player]
            )

        if len(changed_card_positions) < 2:
            # normal
            self.board[board_index] = (card_name, player)
            self.flip(board_index)

        else:
            # combo
            for pos in changed_card_positions:
                if pos != board_index:
                    self.board[pos] = (self.board[pos][0], player)

            self.flip_combo(changed_card_positions)

        self.turn_index = 1 - self.turn_index

        if all(tile is not None for tile in self.board):
            self.terminate()

        return True

    def flip(self, curr: int):
        right, up, left, down = (1, -3, -1, 3)

        flipped = []

        # right
        if curr in [0, 1, 3, 4, 6, 7]:
            if self.compare_single(curr, curr + right):
                flipped.append(curr + right)

        # up
        if curr in [3, 4, 5, 6, 7, 8]:
            if self.compare_single(curr, curr + up):
                flipped.append(curr + up)

        # left
        if curr in [1, 2, 4, 5, 7, 8]:
            if self.compare_single(curr, curr + left):
                flipped.append(curr + left)

        # down
        if curr in [0, 1, 2, 3, 4, 5]:
            if self.compare_single(curr, curr + down):
                flipped.append(curr + down)

        for pos in set(flipped):
            c, i = self.board[pos]
            self.board[pos] = (c, 1 - i)

    def flip_combo(self, just_flipped: List[int]):
        right, up, left, down = (1, -3, -1, 3)

        flipped = []

        for curr in just_flipped:
            # right
            if curr in [0, 1, 3, 4, 6, 7]:
                if self.compare_single(curr, curr + right):
                    flipped.append(curr + right)

            # up
            if curr in [3, 4, 5, 6, 7, 8]:
                if self.compare_single(curr, curr + up):
                    flipped.append(curr + up)

            # left
            if curr in [1, 2, 4, 5, 7, 8]:
                if self.compare_single(curr, curr + left):
                    flipped.append(curr + left)

            # down
            if curr in [0, 1, 2, 3, 4, 5]:
                if self.compare_single(curr, curr + down):
                    flipped.append(curr + down)

        for pos in set(flipped):
            c, i = self.board[pos]
            self.board[pos] = (c, 1 - i)

        if flipped != []:
            self.flip_combo(list(set(flipped)))

    def check_same(self, curr: int) -> List[int]:
        result = []
        right, up, left, down = (1, -3, -1, 3)

        # right
        if curr in [0, 1, 3, 4, 6, 7]:
            if self.check_same_single(curr, curr + right):
                result.append(curr + right)

        # up
        if curr in [3, 4, 5, 6, 7, 8]:
            if self.check_same_single(curr, curr + up):
                result.append(curr + up)

        # left
        if curr in [1, 2, 4, 5, 7, 8]:
            if self.check_same_single(curr, curr + left):
                result.append(curr + left)

        # down
        if curr in [0, 1, 2, 3, 4, 5]:
            if self.check_same_single(curr, curr + down):
                result.append(curr + down)

        return result

    def check_plus(self, curr: int) -> List[int]:
        result = []
        right, up, left, down = (1, -3, -1, 3)

        # right
        if curr in [0, 1, 3, 4, 6, 7]:
            result.append((curr + right, self.get_sum_single(curr, curr + right)))

        # up
        if curr in [3, 4, 5, 6, 7, 8]:
            result.append((curr + up, self.get_sum_single(curr, curr + up)))

        # left
        if curr in [1, 2, 4, 5, 7, 8]:
            result.append((curr + left, self.get_sum_single(curr, curr + left)))

        # down
        if curr in [0, 1, 2, 3, 4, 5]:
            result.append((curr + down, self.get_sum_single(curr, curr + down)))

        result = [
            targ
            for (targ, s) in result
            if any(r[1] == s != -1 and r[0] != targ for r in result)
        ]

        return result

    # if curr wins and targs loses, return True
    def compare_single(self, curr: int, targ: int) -> bool:
        right, up, left, down = (0, 1, 2, 3)

        # if one or more are empty, return false
        if self.board[curr] is None or self.board[targ] is None:
            return False

        # if two cards are of same player, return false
        if self.board[curr][1] == self.board[targ][1]:
            return False

        if curr - targ == -1:  # right
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][right]
                > FFTripleTriad.CARDS[self.board[targ][0]][left]
            )
        if curr - targ == 3:  # up
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][up]
                > FFTripleTriad.CARDS[self.board[targ][0]][down]
            )
        if curr - targ == 1:  # left
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][left]
                > FFTripleTriad.CARDS[self.board[targ][0]][right]
            )
        if curr - targ == -3:  # down
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][down]
                > FFTripleTriad.CARDS[self.board[targ][0]][up]
            )

    def check_same_single(self, curr: int, targ: int) -> bool:
        right, up, left, down = (0, 1, 2, 3)

        # if one or more are empty, return false
        if self.board[curr] is None or self.board[targ] is None:
            return False

        if curr - targ == -1:  # right
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][right]
                == FFTripleTriad.CARDS[self.board[targ][0]][left]
            )
        if curr - targ == 3:  # up
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][up]
                == FFTripleTriad.CARDS[self.board[targ][0]][down]
            )
        if curr - targ == 1:  # left
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][left]
                == FFTripleTriad.CARDS[self.board[targ][0]][right]
            )
        if curr - targ == -3:  # down
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][down]
                == FFTripleTriad.CARDS[self.board[targ][0]][up]
            )

    def get_sum_single(self, curr: int, targ: int) -> int:
        right, up, left, down = (0, 1, 2, 3)

        if self.board[curr] is None or self.board[targ] is None:
            return -1

        if curr - targ == -1:  # right
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][right]
                + FFTripleTriad.CARDS[self.board[targ][0]][left]
            )
        if curr - targ == 3:  # up
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][up]
                + FFTripleTriad.CARDS[self.board[targ][0]][down]
            )
        if curr - targ == 1:  # left
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][left]
                + FFTripleTriad.CARDS[self.board[targ][0]][right]
            )
        if curr - targ == -3:  # down
            return (
                FFTripleTriad.CARDS[self.board[curr][0]][down]
                + FFTripleTriad.CARDS[self.board[targ][0]][up]
            )

    @staticmethod
    def insert_image(basename: str, column: int, row: int) -> str:
        return image.use_image(
            os.environ.get("ASSETS_PATH", "") + "/ff_tt/" + basename + ".png",
            tx=12 + 268 * row,
            ty=12 + 268 * column,
        )

    def print_hand(self, index: int) -> str:
        hand = self.hands[index]
        gen_path = lambda i: (
            f"""<path d="{image.get_rounded_square_path(256, 256, 16, cx=140 + 268 * i, cy=224)}" style="stroke:none;fill:#EBEBEB;stroke-miterlimit:10;" />"""
        )
        gen_text = lambda i: (
            f"""
            <text style='font-family:Noto Sans CJK KR;font-size:64px;font-style:normal;fill:#fff;fill-opacity:1;stroke:#4d4d4d;stroke-width:12px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1' dominant-baseline="middle" text-anchor="middle" transform="matrix(1,0,0,1,{140 + i * 268},32)">{i + 1}</text>
            <text style='font-family:Noto Sans CJK KR;font-size:64px;font-style:normal;fill:#fff;fill-opacity:1' dominant-baseline="middle" text-anchor="middle" transform="matrix(1,0,0,1,{140 + i * 268},32)">{i + 1}</text>
            """
        )
        return image.render_svg(
            1352,
            350,
            defs=[
                image.get_image_def(
                    os.environ.get("ASSETS_PATH", "")
                    + "/ff_tt/"
                    + FFTripleTriad.tile_to_str((hand[i], index))
                    + ".png"
                )
                for i in range(5)
                if hand[i] is not None
            ],
            inner=[
                *[gen_text(i) for i in range(5)],
                *[gen_path(i) for i in range(5) if hand[i] is None],
                *[
                    FFTripleTriad.insert_image(
                        FFTripleTriad.tile_to_str((hand[i], index)), 72 / 268, i
                    )
                    for i in range(5)
                    if hand[i] is not None
                ],
            ],
        )

    def print_board(self) -> str:
        gen_path = lambda i: (
            f"""<path d="{image.get_rounded_square_path(256, 256, 16, cx=140 + 268 * (i % 3), cy=140 + 268 * (i // 3))}" style="stroke:none;fill:#EBEBEB;stroke-miterlimit:10;" />"""
        )
        gen_text = (
            lambda i: f"""
            <text xmlns="http://www.w3.org/2000/svg" style='font-family:Noto Sans CJK KR;font-size:72px;font-style:normal;fill:#373737;stroke:none;' dominant-baseline="middle" text-anchor="middle" transform="matrix(1,0,0,1,{268 * (i % 3) + 140},{268 * (i // 3) + 140 - 4})">{chr(65 + i)}</text>
            """
        )

        return image.render_svg(
            816,
            816,
            defs=[
                image.get_image_def(
                    os.environ.get("ASSETS_PATH", "")
                    + "/ff_tt/"
                    + FFTripleTriad.tile_to_str(self.board)
                    + ".png"
                )
                for i in range(9)
                if self.board[i] is not None
            ],
            inner=[
                *[gen_path(i) for i in range(9) if self.board[i] is None],
                *[gen_text(i) for i in range(9) if self.board[i] is None],
                *[
                    FFTripleTriad.insert_image(
                        FFTripleTriad.tile_to_str(tile), i // 3, i % 3
                    )
                    for (i, tile) in enumerate(self.board)
                    if tile is not None
                ],
            ],
        )
