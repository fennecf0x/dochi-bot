from typing import List, TypedDict, TypeVar, Generic, Hashable
import random
import time
import math
import gmpy2
from gmpy2 import mpz
import discord
from .item import CommandItem
from dochi.state import state


def modulo_exp(x: int, e: int, m: int) -> int:
    """
    returns x^e mod m
    """

    X = x
    E = e
    Y = 1
    while E > 0:
        if E % 2 == 0:
            X = (X * X) % m
            E = E / 2
        else:
            Y = (X * Y) % m
            E = E - 1
    return Y


def get_partial_sum(n: int, j: int) -> float:
    """
    returns the fractional part of 16^n S_j

    {16^n S_j}
        = {
            {\sum_{k=0}^n (16^(n - k) mod 8k + j) / (8k + j)}
            + \sum_{k=n+1}^\infty 16^(n - k) / (8k + j)
        }

    where S_j = \sum_{k=0}^\infty 1 / (16^k (8k + j))
    """
    first_term = sum(
        modulo_exp(16, n - k, 8 * k + j) / (8 * k + j) for k in range(0, n + 1)
    )
    first_term = first_term - math.floor(first_term)

    k = n + 1
    second_term = 0
    while True:
        max_rest_term = 16 ** (n - k) / max(8 * k, 1) / 15
        if math.floor(second_term * 16) == math.floor(
            (second_term + max_rest_term) * 16
        ):
            break

        second_term += 16 ** (n - k) / (8 * k + j)
        k += 1

    res = first_term + second_term
    res = res - math.floor(res)

    return res


def get_nth_digit_hex(n: int) -> int:
    """
    returns the first digit of {16^n \pi}, which is
    {4 {16^n S_1} - 2 {16^n S_4} - {16^n S_5} - {16^n S_6}}
    """
    res = (
        4 * get_partial_sum(n, 1)
        - 2 * get_partial_sum(n, 4)
        - get_partial_sum(n, 5)
        - get_partial_sum(n, 6)
    )
    res = res - math.floor(res)

    return math.floor(res * 16)


# Credit: https://www.craig-wood.com/nick/articles/pi-chudnovsky/
def pi_chudnovsky_bs(digits):
    """
    Compute int(pi * 10**digits)

    This is done using Chudnovsky's series with binary splitting
    """
    C = 640320
    C3_OVER_24 = C**3 // 24
    def bs(a, b):
        """
        Computes the terms for binary splitting the Chudnovsky infinite series

        a(a) = +/- (13591409 + 545140134*a)
        p(a) = (6*a-5)*(2*a-1)*(6*a-1)
        b(a) = 1
        q(a) = a*a*a*C3_OVER_24

        returns P(a,b), Q(a,b) and T(a,b)
        """
        if b - a == 1:
            # Directly compute P(a,a+1), Q(a,a+1) and T(a,a+1)
            if a == 0:
                Pab = Qab = mpz(1)
            else:
                Pab = mpz((6*a-5)*(2*a-1)*(6*a-1))
                Qab = mpz(a*a*a*C3_OVER_24)
            Tab = Pab * (13591409 + 545140134*a) # a(a) * p(a)
            if a & 1:
                Tab = -Tab
        else:
            # Recursively compute P(a,b), Q(a,b) and T(a,b)
            # m is the midpoint of a and b
            m = (a + b) // 2
            # Recursively calculate P(a,m), Q(a,m) and T(a,m)
            Pam, Qam, Tam = bs(a, m)
            # Recursively calculate P(m,b), Q(m,b) and T(m,b)
            Pmb, Qmb, Tmb = bs(m, b)
            # Now combine
            Pab = Pam * Pmb
            Qab = Qam * Qmb
            Tab = Qmb * Tam + Pam * Tmb
        return Pab, Qab, Tab
    # how many terms to compute
    DIGITS_PER_TERM = math.log10(C3_OVER_24/6/2/6)
    N = int(digits/DIGITS_PER_TERM + 1)
    # Calclate P(0,N) and Q(0,N)
    P, Q, T = bs(0, N)
    one_squared = mpz(10)**(2*digits)
    sqrtC = gmpy2.isqrt(10005*one_squared)
    return (Q*426880*sqrtC) // T


class GetNthDigitOfPi(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        n: int = 1,
        base: int = 10,
        **kwargs,
    ):
        """
        Get n-th digit of \pi (in base 10 or 16)

        Example: n = 0 -> 3, n = 1 -> 1, n = 2 -> 4, ...
        """

        if base not in [10, 16] or n < 0:
            return kwargs

        if base == 10 and n > 1000000:
            digit = "🥲"

        elif base == 10:
            digit = str(pi_chudnovsky_bs(n))
            digit = digit[-1]

        elif base == 16:
            digit = "%X" % get_nth_digit_hex(n - 1) if n >= 1 else 3

        return {**kwargs, "digit": digit}
