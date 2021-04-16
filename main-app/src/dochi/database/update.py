"""
update.py

Utils for updating database
"""

from typing import Optional
import time

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


def currency_info(
    currency_type: CurrencyType,
    *,
    price: float,
    timer_inc: float,
    timer_inc_thres: float,
    timer_dec: float,
    timer_dec_thres: float,
    ewma1: float,
    ewma2: float,
    ewma2_flag: float,
) -> model.CurrencyInfo:
    try:
        currency_info = model.CurrencyInfo.get(currency_type=currency_type.name)
        currency_info.price = price
        currency_info.timer_inc = timer_inc
        currency_info.timer_inc_thres = timer_inc_thres
        currency_info.timer_dec = timer_dec
        currency_info.timer_dec_thres = timer_dec_thres
        currency_info.ewma1 = ewma1
        currency_info.ewma2 = ewma2
        currency_info.ewma2_flag = ewma2_flag
        currency_info.save()

        return currency_info

    except model.CurrencyInfo.DoesNotExist:  # pylint: disable=maybe-no-member
        currency_info = model.CurrencyInfo.create(
            currency_type=currency_type.name,
            price=price,
            timer_inc=timer_inc,
            timer_inc_thres=timer_inc_thres,
            timer_dec=timer_dec,
            timer_dec_thres=timer_dec_thres,
            ewma1=ewma1,
            ewma2=ewma2,
            ewma2_flag=ewma2_flag,
        )

        return currency_info


def currency_price_record(
    currency_type: CurrencyType, *, timestamp: float, price: float
) -> model.CurrencyPriceRecord:
    currency_price_record = model.CurrencyPriceRecord.create(
        currency_type=currency_type.name,
        timestamp=timestamp,
        price=price,
    )

    return currency_price_record


def drop_old_currency_price_records(days: int):
    time_criterion = time.time() - days * 24 * 60 * 60
    model.CurrencyPriceRecord.delete().where(
        model.CurrencyPriceRecord.timestamp < time_criterion
    ).execute()


def inventory(
    user_id: str,
    *,
    item_type: str,
    amount: int,
    incremental: bool = True,
) -> model.Item:
    try:
        item = model.Item.get(user_id=user_id, item_type=item_type)
        item.amount = item.amount + amount if incremental else amount
        item.save()

        return item

    except model.Item.DoesNotExist:  # pylint: disable=maybe-no-member
        item = model.Item.create(user_id=user_id, item_type=item_type, amount=amount)

        return item


def item_info(
    item_type: str,
    alias: str,
    image: str,
    description: str,
    stackable: bool,
) -> model.ItemInfo:
    try:
        item = model.ItemInfo.get(item_type=item_type)
        item.alias = alias
        item.image = image
        item.description = description
        item.stackable = stackable
        item.save()

        return item

    except model.ItemInfo.DoesNotExist:  # pylint: disable=maybe-no-member
        item = model.ItemInfo.create(
            item_type=item_type,
            alias=alias,
            image=image,
            description=description,
            stackable=stackable,
        )

        return item
