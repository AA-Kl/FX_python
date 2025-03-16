from datetime import date
from typing import Optional
from .currency import Currency
from .direction import PaymentDirection

class Payment:
    def __init__(self, date: date, currency: Currency, amount: float, direction: PaymentDirection = None, amount_usd: Optional[float] = None):
        self.date = date
        self.currency = currency
        self.amount = amount
        self.direction = direction
        self.amount_usd = amount_usd

    def __str__(self):
        amount_usd_str = f",\n amount_usd={self.amount_usd}" if self.amount_usd is not None else ""
        return (
            f"  Payment(\n"
            f"      date={self.date},\n"
            f"      currency={self.currency},\n"
            f"      amount={self.amount},\n"
            f"      direction={self.direction}{amount_usd_str})"
        )  