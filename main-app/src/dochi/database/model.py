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


class CurrencyInfo(Base):
    """
    Currency price varying info:

    * price
    * timer_inc
    * timer_inc_thres
    * timer_dec
    * timer_dec_thres
    * ewma1
    * ewma2
    * ewma2_flag
    """

    """currency type: string"""
    currency_type = peewee.TextField()

    price = peewee.FloatField()
    timer_inc = peewee.FloatField()
    timer_inc_thres = peewee.FloatField()
    timer_dec = peewee.FloatField()
    timer_dec_thres = peewee.FloatField()
    ewma1 = peewee.FloatField()
    ewma2 = peewee.FloatField()
    ewma2_flag = peewee.FloatField()


class CurrencyPriceRecord(Base):
    """
    Currency price records:

    * currency_type
    * price
    * timestamp
    """

    """currency type: string"""
    currency_type = peewee.TextField()
    price = peewee.FloatField()
    timestamp = peewee.FloatField()


class Item(Base):
    """
    Item model
    """

    """User: User"""
    user = peewee.ForeignKeyField(User, backref="inventory")

    """item type: string"""
    item_type = peewee.TextField()

    """amount: int"""
    amount = peewee.IntegerField(default=1)

    """aux: string (stringified JSON)"""
    aux = peewee.TextField(default="")


class ItemInfo(Base):
    """
    ItemInfo model
    """

    """item type: string"""
    item_type = peewee.TextField()

    """alias: string `|alias_1|alias_2|...|alias_n|`"""
    alias = peewee.TextField(default="|")

    """image: string"""
    image = peewee.TextField()

    """description: string"""
    description = peewee.TextField()

    """stackable: bool"""
    stackable = peewee.BooleanField()
