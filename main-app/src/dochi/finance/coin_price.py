"""
manage coin prices
"""


from dataclasses import dataclass
import numpy as np
import math
import time
from ..database.types import CurrencyType
from ..database import update, get
from ..state import state, DictX


@dataclass
class CoinPriceConstants:
    BASE_PRICE: float

    TIME_SLICE_LOW: float
    TIME_SLICE_HIGH: float

    TIMER_INC_DEC_FACTOR: float
    TIMER_DEC_DEC_FACTOR: float

    TIMER_INC_LOW: float
    TIMER_INC_HIGH: float
    TIMER_DEC_LOW: float
    TIMER_DEC_HIGH: float

    TIMER_INC_THRES_LOW: float
    TIMER_INC_THRES_HIGH: float
    TIMER_DEC_THRES_LOW: float
    TIMER_DEC_THRES_HIGH: float

    PRICE_BIG_NOISE_FACTOR: float
    PRICE_SMALL_NOISE_FACTOR: float

    EWMA_HIGH_THRES_LOW: float
    EWMA_HIGH_THRES_HIGH: float
    EWMA_LOW_THRES_LOW: float
    EWMA_LOW_THRES_HIGH: float

    ALPHA1: float
    ALPHA2: float


@dataclass
class CoinPriceParams:
    price: float

    # varying params
    timer_inc: float
    timer_inc_thres: float
    timer_dec: float
    timer_dec_thres: float
    ewma1: float
    ewma2: float
    ewma2_flag: bool


def update_coin_params(currency_type: CurrencyType, coin_params: CoinPriceParams):
    update.currency_info(
        currency_type,
        price=coin_params.price,
        timer_inc=coin_params.timer_inc,
        timer_inc_thres=coin_params.timer_inc_thres,
        timer_dec=coin_params.timer_dec,
        timer_dec_thres=coin_params.timer_dec_thres,
        ewma1=coin_params.ewma1,
        ewma2=coin_params.ewma2,
        ewma2_flag=coin_params.ewma2_flag,
    )


def initialize_coin_params(
    currency_type: CurrencyType, coin_constants: CoinPriceConstants
) -> CoinPriceParams:
    currency_info = get.currency_info(currency_type)
    if currency_info is not None:
        return DictX({
            "price": currency_info.price,
            "timer_inc": currency_info.timer_inc,
            "timer_inc_thres": currency_info.timer_inc_thres,
            "timer_dec": currency_info.timer_dec,
            "timer_dec_thres": currency_info.timer_dec_thres,
            "ewma1": currency_info.ewma1,
            "ewma2": currency_info.ewma2,
            "ewma2_flag": currency_info.ewma2_flag,
        })

    coin_params: CoinPriceParams = DictX({
        "price": coin_constants.BASE_PRICE,
        "timer_inc": np.random.uniform(
            low=coin_constants.TIMER_INC_LOW, high=coin_constants.TIMER_INC_HIGH
        ),
        "timer_inc_thres": 0,
        "timer_dec": np.random.uniform(
            low=coin_constants.TIMER_DEC_LOW, high=coin_constants.TIMER_DEC_HIGH
        ),
        "timer_dec_thres": 0,
        "ewma1": coin_constants.BASE_PRICE,
        "ewma2": coin_constants.BASE_PRICE,
        "ewma2_flag": 0,
    })

    update_coin_params(currency_type, coin_params)

    return coin_params


def update_price(
    coin_constants: CoinPriceConstants, coin_params: CoinPriceParams, time_multiple=1
):
    delta_t = np.random.uniform(
        low=coin_constants.TIME_SLICE_LOW, high=coin_constants.TIME_SLICE_HIGH
    )

    if coin_params.timer_inc_thres > 0:
        coin_params.timer_inc_thres -= (
            abs(np.random.normal()) * coin_constants.TIMER_INC_DEC_FACTOR * delta_t
        )
        coin_params.price += (
            np.random.gamma(1.5)
            * coin_params.price
            * np.random.uniform(low=0.05, high=0.09)
            / 200
        )

    if coin_params.timer_dec_thres > 0:
        coin_params.timer_dec_thres -= (
            abs(np.random.normal()) * coin_constants.TIMER_DEC_DEC_FACTOR * delta_t
        )
        coin_params.price -= (
            np.random.gamma(2)
            * coin_params.price
            * np.random.uniform(low=0.05, high=0.09)
            / 150
        )

    gaussian_noises = np.random.normal(size=2)

    coin_params.price += (
        coin_constants.PRICE_BIG_NOISE_FACTOR
        * coin_params.price
        * gaussian_noises[0]
        * delta_t
        / (60 * 60 * 24)
        + coin_constants.PRICE_SMALL_NOISE_FACTOR
        * math.pow(coin_params.price, 0.8)
        * gaussian_noises[1]
        * delta_t
        / 5
    )
    coin_params.price = max(coin_params.price, 0)

    coin_params.ewma1 *= 1 - coin_constants.ALPHA1
    coin_params.ewma1 += coin_constants.ALPHA1 * coin_params.price

    coin_params.ewma2 *= 1 - coin_constants.ALPHA2
    coin_params.ewma2 += coin_constants.ALPHA2 * coin_params.price

    coin_params.timer_inc -= delta_t
    coin_params.timer_dec -= delta_t

    if coin_params.timer_inc < 0:
        coin_params.timer_inc = np.random.uniform(
            low=coin_constants.TIMER_INC_LOW, high=coin_constants.TIMER_INC_HIGH
        )
        coin_params.timer_inc_thres = np.random.gamma(2) * np.random.uniform(
            low=coin_constants.TIMER_INC_THRES_LOW,
            high=coin_constants.TIMER_INC_THRES_HIGH,
        )

    if coin_params.timer_dec < 0:
        coin_params.timer_dec = np.random.uniform(
            low=coin_constants.TIMER_DEC_LOW, high=coin_constants.TIMER_DEC_HIGH
        )
        coin_params.timer_dec_thres = np.random.gamma(2) * np.random.uniform(
            low=coin_constants.TIMER_DEC_THRES_LOW,
            high=coin_constants.TIMER_DEC_THRES_HIGH,
        )

    if coin_params.ewma2_flag > 0:
        delta_price = (
            max(
                np.random.gamma(6)
                * (coin_params.price - coin_params.ewma2)
                * np.random.gamma(shape=1, scale=2) / 200,
                coin_params.price * 0.003,
            )
            / 20
        )
        coin_params.price -= delta_price
        if (
            coin_params.price / coin_params.ewma2
            < coin_constants.EWMA_HIGH_THRES_LOW + np.random.normal() * 0.155
        ):
            coin_params.ewma2_flag = 0

    elif coin_params.ewma2_flag < 0:
        delta_price = (
            max(
                -np.random.gamma(6)
                * (coin_params.price - coin_params.ewma2)
                * np.random.gamma(shape=1, scale=2) / 200,
                coin_params.price * 0.003,
            )
            / 20
        )
        coin_params.price += delta_price
        if (
            coin_params.price / coin_params.ewma2
            > coin_constants.EWMA_LOW_THRES_HIGH + np.random.normal() * 0.155
        ):
            coin_params.ewma2_flag = 0

    elif (
        coin_params.price / coin_params.ewma2
        > coin_constants.EWMA_HIGH_THRES_HIGH + np.random.normal() * 0.225
    ):
        coin_params.ewma2_flag = 1

    elif (
        coin_params.price / coin_params.ewma2
        < coin_constants.EWMA_LOW_THRES_LOW + np.random.normal() * 0.0925
    ):
        coin_params.ewma2_flag = -1

    time.sleep(delta_t / time_multiple)
