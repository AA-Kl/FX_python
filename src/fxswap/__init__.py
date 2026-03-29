"""
FXSwap - A Python library for FX (Foreign Exchange) swap and trade operations.

This package provides classes and utilities for managing FX trades, swaps,
currency pairs, and related payment processing.
"""

from .classes.currency import Currency
from .classes.currency_pair import CurrencyPair
from .classes.direction import TradeDirection, PaymentDirection
from .classes.FXrate import FXrate
from .classes.FXTrade import FXTrade
from .classes.FXSwap import FXSwap
from .classes.payment import Payment
from .classes.calendar import Calendar, RollConvention
from .classes.interest_rate_curve import DayCountConvention, InterpolationMethod, InterestRateCurve

__version__ = "0.1.0"
__all__ = [
    "Currency",
    "CurrencyPair",
    "TradeDirection",
    "PaymentDirection",
    "FXrate",
    "FXTrade",
    "FXSwap",
    "Payment",
    "Calendar",
    "RollConvention",
    "DayCountConvention",
    "InterpolationMethod",
    "InterestRateCurve",
]
