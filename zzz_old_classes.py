# from enum import Enum
# from datetime import datetime

# class Currency(Enum):
#     USD = "USD"
#     EUR = "EUR"
#     GBP = "GBP"
#     JPY = "JPY"
#     AUD = "AUD"
#     CAD = "CAD"

# class CurrencyPair(Enum):
#     EUR_USD = (Currency.EUR, Currency.USD)
#     GBP_USD = (Currency.GBP, Currency.USD)
#     USD_JPY = (Currency.USD, Currency.JPY)
#     AUD_USD = (Currency.AUD, Currency.USD)
#     USD_CAD = (Currency.USD, Currency.CAD)

#     # Additional pairs
#     EUR_GBP = (Currency.EUR, Currency.GBP)
#     EUR_JPY = (Currency.EUR, Currency.JPY)
#     GBP_JPY = (Currency.GBP, Currency.JPY)
#     AUD_JPY = (Currency.AUD, Currency.JPY)
#     CAD_JPY = (Currency.CAD, Currency.JPY)
#     GBP_CAD = (Currency.GBP, Currency.CAD)
#     AUD_CAD = (Currency.AUD, Currency.CAD)
#     EUR_AUD = (Currency.EUR, Currency.AUD)
#     USD_CHF = (Currency.USD, Currency.CHF)  # Example: Add CHF if defined in Currency Enum

#     def __str__(self):
#         base, domestic = self.value
#         return f"{base.value}/{domestic.value}"

# class Direction(Enum):
#     BUY = "BUY"
#     SELL = "SELL"
#     BUY_SELL = "BUY_SELL"
#     SELL_BUY = "SELL_BUY"

# class Payment:
#     def __init__(self, date: datetime, currency: Currency, amount: float, direction: Direction = None):
#         self.date = date
#         self.currency = currency
#         self.amount = amount
#         self.direction = direction
#         self.amount_usd = self.calculate_amount_usd()

#     def get_exchange_rate(self):
#         for pair, rate in EXCHANGE_RATES.items():
#             if pair.value[0] == self.currency and pair.value[1] == Currency.USD:
#                 return rate
#             elif pair.value[1] == self.currency and pair.value[0] == Currency.USD:
#                 return rate
#         return None

#     def calculate_amount_usd(self):
#         if self.currency == Currency.USD:
#             return self.amount
#         exchange_rate = self.get_exchange_rate()
#         if exchange_rate:
#             for pair in EXCHANGE_RATES.keys():
#                 if pair.value[0] == self.currency and pair.value[1] == Currency.USD:
#                     return self.amount / exchange_rate
#                 elif pair.value[1] == self.currency and pair.value[0] == Currency.USD:
#                     return self.amount * exchange_rate
#         return None

#     def __repr__(self):
#         direction = self.direction.value if self.direction else "None"
#         amount_usd = f"{self.amount_usd:.2f}" if self.amount_usd is not None else "None"
#         return (f"Payment(date={self.date}, currency={self.currency.value}, amount={self.amount:.2f}, "
#                 f"direction={direction}, amount_usd={amount_usd})")

# class FXTrade:
#     def __init__(self, payment_receive: Payment, payment_pay: Payment, currency_pair: CurrencyPair):
#         self.payment_receive = payment_receive
#         self.payment_pay = payment_pay
#         self.currency_pair = currency_pair
#         self.direction = Direction.BUY if payment_receive.currency == currency_pair.value[0] else Direction.SELL

#     def __repr__(self):
#         return (f"FXTrade(receive={self.payment_receive}, pay={self.payment_pay}, "
#                 f"direction={self.direction.value}, currency_pair={str(self.currency_pair)})")

# class FXSwap:
#     def __init__(self, fx_trade_near: FXTrade, fx_trade_far: FXTrade):
#         if fx_trade_near.direction == fx_trade_far.direction:
#             raise ValueError("FXSwap trades must have opposite directions")
#         if fx_trade_near.payment_receive.date == fx_trade_far.payment_receive.date:
#             raise ValueError("FXSwap trades must have different payment dates")
#         self.fx_trade_near = fx_trade_near
#         self.fx_trade_far = fx_trade_far
#         self.direction = Direction.BUY_SELL if fx_trade_near.direction == Direction.BUY else Direction.SELL_BUY

#     def __repr__(self):
#         return (f"FXSwap(near_leg={self.fx_trade_near}, far_leg={self.fx_trade_far}, direction={self.direction.value})")
