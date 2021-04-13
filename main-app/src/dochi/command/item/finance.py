from typing import Tuple, Union, Optional, cast
from typing_extensions import TypedDict, Literal
import asyncio
import re
import os
import time
import tempfile
import math
import tossi
import numpy as np
import discord
from .item import CommandItem
from ..patterns import 줘, 게, 했
from ...database import get, update
from ...database.types import CurrencyType, currency_name_type, currency_type_ko
from ...state import state

from pygnuplot import gnuplot
import pandas as pd


"""
Committing transaction
"""


class TransactionReturnType(TypedDict):
    currency_type: CurrencyType
    price_per: Optional[float]
    amount: Optional[Tuple[float, Literal["개", "원"]]]
    transaction_type: Literal["BUY", "SELL"]


def extract_transaction_data(string: str) -> Optional[TransactionReturnType]:
    pattern = rf"^([가-힣A-Za-z]*?)((0|[1-9]\d*)(\.\d*)?)원(일때|에서|에)((((0|[1-9]\d*)(\.\d*)?)개)만?|(((0|[1-9]\d*)(\.\d*)?)원(어?치|만큼))만?|전부|전체|모두|다)(((매수|구매)(해{줘}?|할래|할{게}|하자|하고싶어)?|살래|살{게}|사고싶어|사자)|((매도|매각|판매)(해{줘}?|할래|할{게}|하자|하고싶어)?|팔래|팔{게}|팔아{줘}?|팔고싶어))$"
    match = re.match(pattern, string)

    if match is not None:
        (currency_name, price_per, total_amount, total_price, is_buying) = match.group(
            1, 2, 8, 12, 17
        )

    else:
        pattern = rf"^([가-힣A-Za-z]*?)?(지금)?(바로|즉시)?((((0|[1-9]\d*)(\.\d*)?)개)만?|(((0|[1-9]\d*)(\.\d*)?)원(어?치|만큼))만?|전부|전체|모두|다)(((매수|구매)(해{줘}?|할래|할{게}|하자|하고싶어)?|살래|살{게}|사고싶어|사자)|((매도|매각|판매)(해{줘}?|할래|할{게}|하자|하고싶어)?|팔래|팔{게}|팔아{줘}?|팔고싶어))$"
        match = re.match(pattern, string)

        print(match)

        if match is None:
            return None

        price_per = None
        print(match.groups())
        (currency_name, total_amount, total_price, is_buying) = match.group(
            1, 6, 10, 15
        )

    currency_type = currency_name_type(currency_name)
    if currency_type is None:
        return None

    return {
        "currency_type": currency_type,
        "price_per": float(price_per) if price_per is not None else None,
        "amount": (
            float(total_amount or total_price),
            "개" if total_price is None else "원",
        ) if (total_amount or total_price) is not None else None,
        "transaction_type": "BUY" if is_buying is not None else "SELL",
    }


class IsTransacting(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        data = extract_transaction_data(content)

        if data is None:
            return {**kwargs, "is_satisfied": False}

        print(data)

        return {**kwargs, "is_satisfied": True, **data}


class TransactCurrency(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        currency_type: CurrencyType,
        price_per: Optional[float],
        amount: Optional[Tuple[float, Literal["개", "원"]]],
        transaction_type: Literal["BUY", "SELL"],
        **kwargs,
    ):
        if currency_type not in state.coin_params:
            return {**kwargs, "content": "아직 상장되지 않은 코인이야!"}

        if price_per is not None:
            # TODO: support buying/selling offer (reservation)
            return {**kwargs, "content": "아직 지원되지 않는 기능이야."}

        current_price_per = state.coin_params[currency_type].price
        if current_price_per <= 0:
            return {**kwargs, "content": "휴지조각이 된 코인이야!"}

        # check if the user has enough currencies to transact

        # change
        currencies = get.currencies(str(message.author.id))
        money_currency = next(
            (currency for currency in currencies if currency.currency_type == "MONEY"),
            None,
        )
        user_money = money_currency.amount if money_currency is not None else 0
        coin_currency = next(
            (
                currency
                for currency in currencies
                if currency.currency_type == currency_type.name
            ),
            None,
        )
        user_coin = coin_currency.amount if coin_currency is not None else 0

        if amount is None:
            if transaction_type == "BUY":
                money_required = user_money
                coin_required = money_required / current_price_per
            else:
                coin_required = user_coin
                money_required = coin_required * current_price_per
        else:
            money_required = (
                amount[0] if amount[1] == "원" else amount[0] * current_price_per
            )
            coin_required = money_required / current_price_per

        if transaction_type == "BUY" and user_money < money_required:
            return {**kwargs, "content": "돈이 부족해 :sob:"}

        if transaction_type == "SELL" and user_coin < coin_required:
            return {**kwargs, "content": "코인이 부족해 :sob:"}

        sign = -1 if transaction_type == "BUY" else 1

        update.currency(
            str(message.author.id),
            currency_type=CurrencyType.MONEY,
            amount=user_money + sign * money_required,
        )

        update.currency(
            str(message.author.id),
            currency_type=currency_type,
            amount=user_coin - sign * coin_required,
        )

        return {
            **kwargs,
            "content": ("매수" if transaction_type == "BUY" else "매도") + " 완료!",
        }


"""
Cancelling transaction
"""


class CancellationReturnType(TypedDict):
    recent: bool
    cancellation_type: Literal["BUY", "SELL"]


def extract_cancellation_data(string: str) -> Optional[CancellationReturnType]:
    pattern = rf"^((방금|금방)({했}던|한)?|아까({했}던|한)?)?((매수|구매)|(매각|매도|판매))취소(해{줘}?|할래|할{게}|하자|하고싶어)?$"
    match = re.match(pattern, string)

    if match is None:
        return None

    (is_cancelling_recent, is_cancelling_buying) = match.group(1, 8)
    return {
        "recent": is_cancelling_recent is not None,
        "cancellation_type": "BUY" if is_cancelling_buying is not None else "SELL",
    }


class IsCancellingTransaction(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        data = extract_cancellation_data(content)

        if data is None:
            return {**kwargs, "is_satisfied": False}

        return {**kwargs, "is_satisfied": True, **data}


def extract_check_wallet_data(string: str) -> bool:
    pattern = r"^([나내]?(지갑|예산)좀?(보여줘|볼래|볼게)?|([나내]?(지갑에?)?)(돈|예산)얼마(야|나?있어))$"
    return cast(bool, re.search(pattern, string))


class IsCheckingWallet(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        return {**kwargs, "is_satisfied": extract_check_wallet_data(content)}


class ChangeFinance(CommandItem):
    def __init__(
        self,
        currency_type: Optional[CurrencyType] = None,
        amount: Optional[float] = None,
        incremental: Optional[bool] = None,
    ):
        self.currency_type = currency_type
        self.amount = amount
        self.incremental = incremental

    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        user_id: Optional[int] = None,
        currency_type: Optional[CurrencyType] = None,
        amount: Optional[float] = None,
        incremental: Optional[bool] = None,
        **kwargs,
    ):
        user_id = str(user_id or message.author.id)
        currency_type = currency_type or self.currency_type
        amount = amount or self.amount
        incremental = incremental or self.incremental

        base = 0

        if incremental:
            currencies = get.currencies(user_id)
            money_currency = next(
                (
                    currency
                    for currency in currencies
                    if currency.currency_type == currency_type.name
                ),
                None,
            )
            base = money_currency.amount if money_currency is not None else 0

        update.currency(
            user_id,
            currency_type=currency_type,
            amount=max(base + amount, 0),
        )

        return kwargs


class DonateMoney(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        user_id: int,
        amount: float,
        currency_type: CurrencyType = CurrencyType.MONEY,
        **kwargs,
    ):
        currency_type = currency_type or self.currency_type
        amount = amount or self.amount

        base = 0

        author_currencies = get.currencies(str(message.author.id))
        author_currency = next(
            (
                currency
                for currency in author_currencies
                if currency.currency_type == currency_type.name
            ),
            None,
        )
        author_currency = author_currency.amount if author_currency is not None else 0

        if author_currency < amount:
            return {**kwargs, "content": "전달할 돈이 없넹"}

        update.currency(
            str(message.author.id),
            currency_type=currency_type,
            amount=max(author_currency - amount, 0),
        )

        # receive
        receiver_currencies = get.currencies(str(user_id))
        receiver_currency = next(
            (
                currency
                for currency in receiver_currencies
                if currency.currency_type == currency_type.name
            ),
            None,
        )
        receiver_currency = (
            receiver_currency.amount if receiver_currency is not None else 0
        )

        update.currency(
            str(user_id),
            currency_type=currency_type,
            amount=max(receiver_currency + amount, 0),
        )

        return {**kwargs, "content": "전달햇어"}


class CheckWallet(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        currencies = get.currencies(str(message.author.id))

        def refine_amount(currency):
            if currency.currency_type == "MONEY":
                return math.floor(currency.amount)

            if currency.amount == 0:
                return 0

            exp = 10 ** max(0, 7 - math.ceil(math.log10(currency.amount)))
            return math.floor(currency.amount * exp) / exp

        currencies = [currency for currency in currencies if refine_amount(currency) > 0]

        if currencies == []:
            content = "돈이 없어"

        else:
            print([(c.amount, c.currency_type) for c in  currencies])

            content = (
                ", ".join(
                    f"{tossi.postfix(currency_type_ko(currency_name_type(currency.currency_type)), '이')} {refine_amount(currency)}{'원' if currency.currency_type == 'MONEY' else '개'}"
                    for currency in currencies
                    if refine_amount(currency) > 0
                )
                + " 있어"
            )

        return {**kwargs, "content": content}


class IsCheckingCurrencyPrice(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        pattern = rf"^(.*?)(((최근)?(가격|그래프|시세)|(가격|그래프|시세)최근)?(((1?[1-9]|2[0-4])시간)|([1-9]|[1-5][0-9])분)?|(최근)?(((1?[1-9]|2[0-4])시간)|([1-9]|[1-5][0-9])분)?(가격|그래프|시세)?)(알려{줘})?$"
        match = re.match(pattern, content)

        if match is None:
            return {**kwargs, "is_satisfied": False}

        (currency_name, hours_1, hours_2, minutes_1, minutes_2) = match.group(
            1, 9, 14, 10, 15
        )

        currency_type = currency_name_type(currency_name)
        if currency_type is None:
            return {**kwargs, "is_satisfied": False}

        if (hours_1 or hours_2) is not None:
            minutes = 60 * int(hours_1 or hours_2)

        elif (minutes_1 or minutes_2) is not None:
            minutes = int(minutes_1 or minutes_2)

        else:
            minutes = 60

        print(currency_type, minutes)

        return {
            **kwargs,
            "is_satisfied": True,
            "currency_type": currency_type,
            "minutes": minutes,
        }


class CheckCurrencyPrice(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        currency_type: CurrencyType,
        minutes: float,  # in minutes
        **kwargs,
    ):
        timestamp = time.time()
        currency_records = get.currency_price_record(currency_type)
        currency_records = [
            (timestamp - currency_record.timestamp, currency_record.price)
            for currency_record in currency_records
            if currency_record.currency_type == currency_type.name
            and currency_record.timestamp > timestamp - 60 * minutes
        ]

        g = gnuplot.Gnuplot(log=True)
        timestamps = [-round(r[0]) / 60 for r in currency_records]
        prices = [r[1] for r in currency_records]

        if timestamps == [] or prices == []:
            return {**kwargs, "content": "데이터가 없어!"}

        with tempfile.NamedTemporaryFile(suffix=".png") as temp_png:
            df = pd.DataFrame(data={"prices": prices}, index=timestamps)
            g.set(
                "palette defined (" + \
                ", ".join(
                    f"{i + 1} '{color}'" 
                    for (i, color)
                    in enumerate(state.coin_constants[currency_type].COLORS)
                ) + ")"
            )
            g.unset("colorbox")
            g.plot_data(
                df,
                'using 1:2:1 with line lw 2 lc palette',
                term="pngcairo size 720,480",
                out='"' + temp_png.name + '"',
                title=f'"{currency_type_ko(currency_type)} 최근 {minutes}분 그래프"',
                xlabel='"Minutes"',
                xrange=f"[{-minutes}:0]",
                key=None,
                size="1, 1",
                origin="0, 0",
            )

            count = 50
            while count > 0:
                print(count, os.stat(temp_png.name).st_size)
                if os.stat(temp_png.name).st_size == 0:
                    count -= 1
                    await asyncio.sleep(0.3)
                else:
                    size = os.stat(temp_png.name).st_size
                    await asyncio.sleep(0.7)
                    if os.stat(temp_png.name).st_size == size:
                        await message.channel.send(file=discord.File(temp_png.name))
                        count = 0
                    else:
                        await asyncio.sleep(0.3)
                        count += 1


        # do not proceed afterward
        return {**kwargs, "is_satisfied": False}
