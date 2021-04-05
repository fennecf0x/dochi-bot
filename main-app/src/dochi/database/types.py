from enum import Enum
from typing import Optional


class CurrencyType(Enum):
    MONEY = 0
    DOCHI_COIN = 1
    HONEYWORKS_CASH = 2
    AYACHISAAYA = 3
    YEONOO = 4
    FFXIV = 5


def currency_type_ko(currency_type: CurrencyType) -> str:
    if currency_type == CurrencyType.MONEY:
        return "돈"
    if currency_type == CurrencyType.DOCHI_COIN:
        return "도치코인"
    if currency_type == CurrencyType.HONEYWORKS_CASH:
        return "허니웍스캐시"
    if currency_type == CurrencyType.AYACHISAAYA:
        return "아야치사아야"
    if currency_type == CurrencyType.YEONOO:
        return "연오코인"
    if currency_type == CurrencyType.FFXIV:
        return "파이널판타지XIV"

    return "Unknown currency"


def currency_name_type(currency_name: str) -> Optional[CurrencyType]:
    if currency_name == "MONEY":
        return CurrencyType.MONEY
    if currency_name == "DOCHI_COIN":
        return CurrencyType.DOCHI_COIN
    if currency_name == "HONEYWORKS_CASH":
        return CurrencyType.HONEYWORKS_CASH
    if currency_name == "AYACHISAAYA":
        return CurrencyType.AYACHISAAYA
    if currency_name == "YEONOO":
        return CurrencyType.YEONOO
    if currency_name == "FFXIV":
        return CurrencyType.FFXIV

    return None


class Likability:
    def __init__(
        self,
        kindliness: float = 0.0,
        unkindliness: float = 0.0,
        friendliness: float = 0.0,
        unfriendliness: float = 0.0,
        respectfulness: float = 0.0,
        disrespectfulness: float = 0.0,
    ):
        self.kindliness: float = kindliness
        self.unkindliness: float = unkindliness
        self.friendliness: float = friendliness
        self.unfriendliness: float = unfriendliness
        self.respectfulness: float = respectfulness
        self.disrespectfulness: float = disrespectfulness

    def __str__(self):
        return (
            "<Likability object\n"
            f"    kindliness: {self.kindliness}\n"
            f"    unkindliness: {self.unkindliness}\n"
            f"    friendliness: {self.friendliness}\n"
            f"    unfriendliness: {self.unfriendliness}\n"
            f"    respectfulness: {self.respectfulness}\n"
            f"    disrespectfulness: {self.disrespectfulness}\n"
            ">"
        )
