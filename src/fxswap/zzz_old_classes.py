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
