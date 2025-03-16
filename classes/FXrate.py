from .currency_pair import CurrencyPair  # Assuming the class is named CurrencyPair
from datetime import datetime, date  # Updated import for date

class FXrate:
    def __init__(self, currencypair: CurrencyPair, datetime_of_rate: datetime, value_date: date):
        self.currencypair = currencypair
        self.datetime_of_rate = datetime_of_rate
        self.value_date = value_date

    def inverted(self):
        inverted_pair = self.currencypair.inverted()  # Assuming CurrencyPair has an inverted method
        inverted_rate = 1 / self.rate  # Assuming `rate` is a property or attribute of FXrate
        return FXrate(inverted_pair, self.datetime_of_rate, self.value_date)
