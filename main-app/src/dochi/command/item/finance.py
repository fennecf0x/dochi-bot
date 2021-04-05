from typing import TypedDict, Tuple, Literal, Union, Optional, cast
import re
import tossi
import numpy as np
import discord
from .item import CommandItem
from ..patterns import 줘, 게, 했
from ...database import get, update
from ...database.types import CurrencyType, currency_name_type, currency_type_ko


"""
Committing transaction
"""


class TransactionReturnType(TypedDict):
    currency_name: str
    price_per: float
    amount: Tuple[float, Literal["개", "원"]]
    transaction_type: Literal["BUY", "SELL"]


def extract_transaction_data(string: str) -> Optional[TransactionReturnType]:
    pattern = rf"^([가-힣A-Za-z]*)((0|[1-9]\d*)(\.\d*)?)원(일때|에서|에)((((0|[1-9]\d*)(\.\d*)?)개)|(((0|[1-9]\d*)(\.\d*)?)원(어치|만큼)))만?(((매수|구매)(해{줘}?|할래|할{게}|하자|하고싶어)?|살래|살{게}|사고싶어|사자)|((매도|매각|판매)(해{줘}?|할래|할{게}|하자|하고싶어)?|팔래|팔{게}|팔아{줘}?|팔고싶어))$"
    match = re.match(pattern, string)

    if match is None:
        return None

    (currency_name, price_per, total_amount, total_price, is_buying) = match.group(
        1, 2, 8, 12, 17
    )

    return {
        "currency_name": currency_name,
        "price_per": float(price_per),
        "amount": (
            float(total_amount or total_price),
            "개" if total_price is None else "원",
        ),
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

        return {**kwargs, "is_satisfied": True, **data}


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
    def __init__(self, currency_type: CurrencyType, amount: float, incremental: bool):
        self.currency_type = currency_type
        self.amount = amount
        self.incremental = incremental

    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        base = 0

        if self.incremental:
            currencies = get.currencies(str(message.author.id))
            money_currency = next(
                (
                    currency
                    for currency in currencies
                    if currency.currency_type == self.currency_type.name
                ),
                None,
            )
            base = money_currency.amount if money_currency is not None else 0

        update.currency(
            str(message.author.id),
            currency_type=self.currency_type,
            amount=base + self.amount,
        )

        return kwargs


class CheckWallet(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        currencies = get.currencies(str(message.author.id))
        if currencies == []:
            content = "돈이 없어" 
        else:
            content = ", ".join(
                f"{tossi.postfix(currency_type_ko(currency_name_type(currency.currency_type)), '이')} {np.format_float_positional(currency.amount, trim='-')}{'원' if currency.currency_type == 'MONEY' else '개'}"
                for currency in currencies
            ) + " 있어"

        return {**kwargs, "content": content}
