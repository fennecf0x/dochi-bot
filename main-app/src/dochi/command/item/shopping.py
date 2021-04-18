"""
inventory.py

all commands related to inventory and items
(do not include store or shopping)
"""

import math
import os
import re
from typing import List, Optional
import discord
import tossi
from ...database import model, get, update
from ...database.types import CurrencyType
from ...util import image, string
from ..command import CommandItem
from ...games.game import SinglePlayerGame
from ..patterns import 줘, 게
from ...state import state


# Buy (as a single player game)
class Shopping(SinglePlayerGame):
    CLOSED = -1
    DEFAULT = 0
    BUYING = 1
    SELLING = 2

    def __init__(self, client: discord.Client, user_id: int):
        super().__init__(client, user_id)
        self.user_id: int = user_id

        self.item_info: Optional[model.ItemInfo] = None
        self.amount: int = 0

        self.item_infos = list(model.ItemInfo.select())

        self.message_dict: dict = {}

        """
        Phase -1: not shown
        Phase 0: default state
        Phase 1: user's buying state
        Phase 2: user's selling state
        + External phase: open/close store
        """
        self.phase: int = Shopping.DEFAULT
        self.page: int = 1

        self.prev_message: Optional[discord.Message] = None

    def play(self, player: int, move: str) -> bool:
        """
        Play a move. The message dict is stored in
        `self.message_dict` whenever a move is valid.
        Here, the move is the message content obtained by
        stripping prepended dochi and any whitespaces.
        """
        if self.phase == Shopping.DEFAULT:
            # 1. exit
            if re.match(r"^(상점)?(나갈래|닫기|종료|끝|그만)$", move):
                self.phase = Shopping.CLOSED
                self.message_dict = {
                    "content": "잘강",
                    "delete": True,
                }
                return True

            # 2. change page
            change_page_match = re.match(r"^상점([1-9]\d*)?$", move)
            if change_page_match is not None:
                page = int(change_page_match.group(1) or 1)
                tot_page = math.ceil(len(self.item_infos) / 24)

                if page > tot_page and self.item_infos != []:
                    # invalid page
                    self.message_dict = {
                        "content": "그런 칸은 없어 :pleading_face:",
                    }
                    return True

                self.page = page
                self.message_dict = {
                    "content": "사고 싶은 게 있으면 '돛 오렌지 2개 구매'처럼 살 수 있어. "
                    + ("상점의 다른 곳을 보려면 '돛 상점 (페이지 수)'를 입력해줘!" if tot_page > 1 else ""),
                    **self.render_store(),
                }
                return True

            # 3. buying/selling
            transact_match = re.match(
                r"^(.*?)(([1-9]\d*)개|하나)?(((구매|구입)(해{줘}?|할래|할{게}|하고싶어)?|살래|살랭|살{게}|사고싶어|{줘})|(판매(해{줘}?|할래|할{게}|하고싶어)?|팔래|팔랭|팔{게}|팔고싶어))$",
                move,
            )
            if transact_match is not None:
                item_alias, amount_str, is_buying = transact_match.group(1, 3, 5)
                amount = int(amount_str or "1")
                is_buying = False if is_buying is None else True

                item_info = next(
                    (item for item in self.item_infos if item_alias == string.strip_whitespaces(item.alias)), None
                )
                if item_info is None:
                    self.message_dict = {
                        "content": "그런 건 안 팔고 잇어 :pensive:",
                    }
                    return True

                if is_buying:
                    # 1. Check if user has enough money
                    user_money = math.floor(
                        next(
                            (
                                currency.amount
                                for currency in get.currencies(self.user_id)
                                if currency.currency_type == CurrencyType.MONEY.name
                            ),
                            0,
                        )
                    )
                    if user_money < item_info.price * amount:

                        self.message_dict = {
                            "content": "돈이 부족하넹 :woozy_face:",
                        }
                        return True

                    self.item_info = item_info
                    self.amount = amount
                    self.message_dict = {
                        "content": f"{tossi.postfix(item_alias, '은')} 하나에 {item_info.price}원이야! {'하나' if amount == 1 else f'{amount}개'} 살래?",
                    }
                    self.phase = Shopping.BUYING
                    return True

                else:
                    # 1. Check if user has enough item
                    user_amount = math.floor(
                        next(
                            (
                                item.amount
                                for item in get.inventory(self.user_id)
                                if item.item_type == item_info.item_type
                            ),
                            0,
                        )
                    )
                    if user_amount < amount:
                        self.message_dict = {
                            "content": f"{tossi.postfix(item_alias, '이')} 부족해! 총 {user_amount}개가 있는 것 같아.",
                        }
                        return True

                    # TODO: DISCOUNT RATE
                    discount_rate = 0.8

                    self.item_info = item_info
                    self.amount = amount
                    self.message_dict = {
                        "content": f"{tossi.postfix(item_alias, '은')} 하나에 {math.floor(discount_rate * item_info.price)}원에 사줄게! {'하나' if amount == 1 else f'{amount}개'} 팔래?",
                    }
                    self.phase = Shopping.SELLING
                    return True

        elif self.phase == Shopping.BUYING:
            if re.match(
                r"^(그럴래|그래|그랭|넹|네|예|넵|넴|넷|ㅇ{1,4}|응{1,2}|웅{1,2}|우웅|사|살래|살랭|살거야|삼|산다|살{게}|사고싶어|{줘})$",
                move,
            ):
                # positive response
                # check if user's money is enough
                user_money = math.floor(
                    next(
                        (
                            currency.amount
                            for currency in get.currencies(self.user_id)
                            if currency.currency_type == CurrencyType.MONEY.name
                        ),
                        0,
                    )
                )
                if user_money < self.item_info.price * self.amount:
                    self.message_dict = {
                        "content": "돈이 부족하넹 :woozy_face:",
                    }

                else:
                    # decrease money
                    update.currency(
                        self.user_id,
                        currency_type=CurrencyType.MONEY,
                        amount=-self.item_info.price * self.amount,
                        incremental=True,
                    )

                    # increase item
                    update.inventory(
                        self.user_id,
                        item_type=self.item_info.item_type,
                        amount=self.amount,
                        incremental=True,
                    )

                    self.message_dict = {
                        "content": "고마워, 또 살 거 있으면 말해줘!",
                        **self.render_store(),
                    }

                self.item_info = None
                self.amount = 0
                self.phase = Shopping.DEFAULT
                return True

            elif re.match(
                r"^(안그럴래|안그래|안그랭|아니|ㄴ{1,4}|노{1,4}|안사|안살래|안살랭|안살거야|안삼|안산다|안살{게}|안사고싶어|사고싶지않아|주지마)$",
                move,
            ):
                # negative response
                self.message_dict = {
                    "content": "알앗어, 사고 싶은 게 생기면 알려줘.",
                    **self.render_store(),
                }

                self.item_info = None
                self.amount = 0
                self.phase = Shopping.DEFAULT
                return True

        elif self.phase == Shopping.SELLING:
            if re.match(
                r"^(그럴래|그래|그랭|넹|네|예|넵|넴|넷|ㅇ{1,4}|응{1,2}|웅{1,2}|우웅|팔아|팔래|팔랭|팔거야|팜|팖|판다|팔{게}|팔고싶어)$",
                move,
            ):
                # positive response
                # check if user's item is enough
                user_amount = math.floor(
                    next(
                        (
                            item.amount
                            for item in get.inventory(self.user_id)
                            if item.item_type == self.item_info.item_type
                        ),
                        0,
                    )
                )
                if user_amount < self.amount:
                    self.message_dict = {
                        "content": "아이템이 부족하넹 :woozy_face:",
                    }

                else:
                    # increase money
                    update.currency(
                        self.user_id,
                        currency_type=CurrencyType.MONEY,
                        amount=self.item_info.price * self.amount,
                        incremental=True,
                    )

                    # increase item
                    update.inventory(
                        self.user_id,
                        item_type=self.item_info.item_type,
                        amount=-self.amount,
                        incremental=True,
                    )

                    self.message_dict = {
                        "content": "고마워, 또 팔고 싶은 거 있으면 말해줘!",
                        **self.render_store(),
                    }

                self.item_info = None
                self.amount = 0
                self.phase = Shopping.DEFAULT
                return True

            elif re.match(
                r"^(안그럴래|안그래|안그랭|아니|ㄴ{1,4}|노{1,4}|안팔아|안팔래|안팔랭|안팔거야|안팖|안팜|안판다|안팔{게}|안팔고싶어|팔고싶지않아)$",
                move,
            ):
                # negative response
                self.message_dict = {
                    "content": "알앗어, 팔고 싶은 게 생기면 알려줘.",
                    **self.render_store(),
                }

                self.item_info = None
                self.amount = 0
                self.phase = Shopping.DEFAULT
                return True

        return False

    def render_store(self) -> dict:
        item_infos = self.item_infos
        page = self.page

        filename = f"{os.environ.get('CACHE_PATH', '')}/items/{page}.png"
        if os.path.exists(filename):
            return {"file": discord.File(filename)}

        WIDTH = 6
        HEIGHT = 4
        NUM = WIDTH * HEIGHT

        item_infos.sort(key=lambda item: item.item_type)
        tot_page = math.ceil(len(item_infos) / NUM)

        item_infos = item_infos[(page - 1) * NUM : page * NUM]
        item_types = set([item.item_type for item in item_infos])

        append_ellipsis = lambda t: t if len(t) < 9 else t[:7] + "…"
        get_text_scale = (
            lambda l: "1,0,0,1"
            if l < 5
            else "0.83, 0, 0, 0.87"
            if l < 7
            else "0.72, 0, 0, 0.82"
        )
        text_style = "font-family:Noto Sans CJK KR;font-style:normal;fill:#5a6e80;fill-opacity:1;stroke:#5a6e80;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
        text_attr = 'dominant-baseline="middle" text-anchor="middle"'

        svg = image.render_svg(
            240 + WIDTH * 196,
            240 + HEIGHT * 196,
            defs=[
                image.get_image_def(
                    f"{os.environ.get('ASSETS_PATH', '')}/items/{item.image}"
                )
                for item in item_infos
            ],
            inner=[
                # wrapper
                f"""<path d="{image.get_squircle_path(240 + WIDTH * 196, 240 + HEIGHT * 196, 120 + WIDTH * 98, 120 + HEIGHT * 98)}" fill="#e1edf7" />""",
                # pagination
                *(
                    [
                        f"""<text style="font-size:48px;font-family:Noto Sans CJK KR;font-style:normal;fill:#5a6e80;fill-opacity:1;stroke:#5a6e80;stroke-width:2px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" {text_attr} transform="matrix(1,0,0,1,{120 + WIDTH * 98},{HEIGHT * 196 + 160})">{page} / {tot_page}</text>"""
                    ]
                    if tot_page > 0
                    else []
                ),
                # placeholders
                *[
                    f"""<circle vector-effect="non-scaling-stroke" cx="{218 + (n % WIDTH) * 196}" cy="{218 + (n // WIDTH) * 196 - 30}" r="32" fill="#cad7ed" />"""
                    for n in range(NUM)
                    if n >= len(item_infos)
                ],
                # item images
                *[
                    image.use_image(
                        f"{os.environ.get('ASSETS_PATH', '')}/items/{item.image}",
                        height=108,
                        tx=218 + (n % WIDTH) * 196,
                        ty=218 + (n // WIDTH) * 196 - 56,
                    )
                    for n, item in enumerate(item_infos)
                ],
                # item labels
                *[
                    f"""<text style="font-size:36px;{text_style}" {text_attr} transform="matrix({get_text_scale(len(
                        item.alias
                    ))},{218 + (n % WIDTH) * 196},{218 + (n // WIDTH) * 196 + 16})">{
                        append_ellipsis(item.alias)
                    }</text>"""
                    for n, item in enumerate(item_infos)
                ],
                *[
                    f"""<text style="font-size:30px;{text_style}" {text_attr} transform="matrix(1,0,0,1,{218 + (n % WIDTH) * 196},{218 + (n // WIDTH) * 196 + 54})">₩{
                        item.price
                    }</text>"""
                    for n, item in enumerate(item_infos)
                ],
            ],
        )

        return {"svg": svg, "tmpfilename": filename}


class StartShopping(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        start shopping
        """

        if (
            kwargs["content"] == "상점"
            and (False, "Shopping", message.author.id) not in state.games
        ):
            game = Shopping(client, message.author.id)
            state.games[game.id] = game


class NotifyShopping(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        send message in shopping
        """

        if (False, "Shopping", message.author.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: Shopping = state.games[(False, "Shopping", message.author.id)]

        message_dict = game.message_dict

        save = False
        if "svg" in message_dict or "file" in message_dict or (
            "delete" in message_dict and message_dict["delete"]
        ):
            save = True
            if game.prev_message is not None:
                await game.prev_message.delete()

        if game.phase == game.CLOSED:
            state.games.pop((False, "Shopping", message.author.id), None)

        return {**kwargs, **message_dict, "save": save}


class PlayShopping(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        move: str,
        **kwargs,
    ):
        """
        play a move in shopping
        """

        if (False, "Shopping", message.author.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: Shopping = state.games[(False, "Shopping", message.author.id)]

        return {**kwargs, "is_satisfied": game.play(None, move)}


class StoreShoppingMessage(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        prev_message: discord.Message,
        **kwargs,
    ):
        """
        store sent message in shopping
        """

        if (False, "Shopping", message.author.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: Shopping = state.games[(False, "Shopping", message.author.id)]

        if kwargs["save"]:
            game.prev_message = prev_message

        return kwargs
