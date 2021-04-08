"""
update.py

Utils for updating database
"""

from typing import List, Optional
import peewee

from .db import db
from ..database import model
from .types import CurrencyType, Likability


def user(user_id: str) -> model.User:
    try:
        with db.atomic():
            return model.User.create(user_id=user_id)
    except peewee.IntegrityError:
        return model.User.get(model.User.user_id == user_id)


def currencies(user_id: str) -> List[model.Currency]:
    return list(user(user_id).currencies)


def currency_info(currency_type: CurrencyType) -> Optional[model.CurrencyInfo]:
    try:
        currency_name = currency_type.name
        return model.CurrencyInfo.get(model.CurrencyInfo.currency_type == currency_name)

    except model.CurrencyInfo.DoesNotExist:  # pylint: disable=maybe-no-member
        return None


def currency_price_record(currency_type: CurrencyType) -> List[model.CurrencyPriceRecord]:
    currency_name = currency_type.name
    return list(model.CurrencyPriceRecord.select().where(model.CurrencyPriceRecord.currency_type == currency_name))


def inventory(user_id: str) -> List[model.Item]:
    return list(user(user_id).inventory)


def likability(user_id: str) -> Likability:
    u = user(user_id)

    return Likability(
        kindliness = u.kindliness,
        unkindliness = u.unkindliness,
        friendliness = u.friendliness,
        unfriendliness = u.unfriendliness,
        respectfulness = u.respectfulness,
        disrespectfulness = u.disrespectfulness,
    )


def likability_from_user(u: model.User) -> Likability:
    return Likability(
        kindliness = u.kindliness,
        unkindliness = u.unkindliness,
        friendliness = u.friendliness,
        unfriendliness = u.unfriendliness,
        respectfulness = u.respectfulness,
        disrespectfulness = u.disrespectfulness,
    )
