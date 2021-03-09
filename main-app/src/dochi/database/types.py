from enum import Enum


class CurrencyType(Enum):
    MONEY = 0
    DOCHI_COIN = 1
    HONEYWORKS_CASH = 2
    AYACHISAAYA = 3
    YEONOO = 4
    FFXIV = 5


def currency_type_ko(currency_type: CurrencyType) -> str:
    if currency_type == CurrencyType.MONEY:
        return '돈'
    if currency_type == CurrencyType.DOCHI_COIN:
        return '도치코인'
    if currency_type == CurrencyType.HONEYWORKS_CASH:
        return '허니웍스캐시'
    if currency_type == CurrencyType.AYACHISAAYA:
        return '아야치사아야'
    if currency_type == CurrencyType.YEONOO:
        return '연오코인'
    if currency_type == CurrencyType.FFXIV:
        return '파이널판타지XIV'

    return "Unknown currency"


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
        return "<Likability object\n" \
            f"    kindliness: {self.kindliness}\n" \
            f"    unkindliness: {self.unkindliness}\n" \
            f"    friendliness: {self.friendliness}\n" \
            f"    unfriendliness: {self.unfriendliness}\n" \
            f"    respectfulness: {self.respectfulness}\n" \
            f"    disrespectfulness: {self.disrespectfulness}\n" \
            ">"
