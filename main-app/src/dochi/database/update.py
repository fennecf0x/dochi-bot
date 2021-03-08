"""
update.py

Utils for updating database
"""

from typing import Optional

from .types import CurrencyType
from ..database import get, model


def likability(
    user_id: str,
    *,
    _kindliness: Optional[float] = None,
    _unkindliness: Optional[float] = None,
    _friendliness: Optional[float] = None,
    _unfriendliness: Optional[float] = None,
    _respectfulness: Optional[float] = None,
    _disrespectfulness: Optional[float] = None,
) -> model.User:
    l = get.likability(user_id=user_id)

    return model.User.replace(
        user_id=user_id,
        kindliness=_kindliness or l.kindliness,
        unkindliness=_unkindliness or l.unkindliness,
        friendliness=_friendliness or l.friendliness,
        unfriendliness=_unfriendliness or l.unfriendliness,
        respectfulness=_respectfulness or l.respectfulness,
        disrespectfulness=_disrespectfulness or l.disrespectfulness,
    ).execute()


def currency(
    user_id: str,
    *,
    currency_type: CurrencyType,
    amount: float,
) -> model.Currency:
    try:
        currency = model.Currency.get(user_id=user_id, currency_type=currency_type.name)
        currency.amount = amount
        currency.save()

        return currency

    except model.Currency.DoesNotExist:
        currency = model.Currency.create(
            user_id=user_id, currency_type=currency_type.name, amount=amount
        )

        return currency
