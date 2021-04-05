"""
update.py

Utils for updating database
"""

from typing import List
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
