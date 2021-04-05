"""
model.py

Database models
"""

import peewee

from .db import db


class Base(peewee.Model):
    class Meta:
        database = db


class User(Base):
    """
    User model
    """

    """User ID: text"""
    user_id = peewee.TextField(unique=True, primary_key=True)

    """
    Likability

    Kindliness / Unkindliness
    Friendliness / Unfriendliness
    Respectfulness / Disrespecfulness
    """
    kindliness = peewee.FloatField(default=0.0)
    unkindliness = peewee.FloatField(default=0.0)

    friendliness = peewee.FloatField(default=0.0)
    unfriendliness = peewee.FloatField(default=0.0)

    respectfulness = peewee.FloatField(default=0.0)
    disrespectfulness = peewee.FloatField(default=0.0)

    # currencies: List[Currency]
    # inventory: List[Item]


class Currency(Base):
    """
    Currency model
    """

    """User: User"""
    user = peewee.ForeignKeyField(User, backref="currencies")

    """currency type: string"""
    currency_type = peewee.TextField()

    """amount: real"""
    amount = peewee.FloatField(default=0.0)


class Item(Base):
    """
    Item model
    """

    """User: User"""
    user = peewee.ForeignKeyField(User, backref="inventory")

    """item type: string"""
    item_type = peewee.TextField()

    """amount: int"""
    amount = peewee.IntegerField(default=0)
