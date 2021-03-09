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
    kindliness: Optional[float] = None,
    unkindliness: Optional[float] = None,
    friendliness: Optional[float] = None,
    unfriendliness: Optional[float] = None,
    respectfulness: Optional[float] = None,
    disrespectfulness: Optional[float] = None,
) -> model.User:
    l = get.likability(user_id=user_id)

    return model.User.replace(
        user_id=user_id,
        kindliness=kindliness or l.kindliness,
        unkindliness=unkindliness or l.unkindliness,
        friendliness=friendliness or l.friendliness,
        unfriendliness=unfriendliness or l.unfriendliness,
        respectfulness=respectfulness or l.respectfulness,
        disrespectfulness=disrespectfulness or l.disrespectfulness,
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

    except model.Currency.DoesNotExist:  # pylint: disable=maybe-no-member
        currency = model.Currency.create(
            user_id=user_id, currency_type=currency_type.name, amount=amount
        )

        return currency
