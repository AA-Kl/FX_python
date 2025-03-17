from enum import Enum
from .currency import Currency

class CurrencyPair(Enum):
    EUR_USD = (Currency.EUR, Currency.USD)
    GBP_USD = (Currency.GBP, Currency.USD)
    USD_JPY = (Currency.USD, Currency.JPY)
    AUD_USD = (Currency.AUD, Currency.USD)
    USD_CAD = (Currency.USD, Currency.CAD)

    # Additional pairs
    EUR_GBP = (Currency.EUR, Currency.GBP)
    EUR_JPY = (Currency.EUR, Currency.JPY)
    GBP_JPY = (Currency.GBP, Currency.JPY)
    AUD_JPY = (Currency.AUD, Currency.JPY)
    CAD_JPY = (Currency.CAD, Currency.JPY)
    GBP_CAD = (Currency.GBP, Currency.CAD)
    AUD_CAD = (Currency.AUD, Currency.CAD)
    EUR_AUD = (Currency.EUR, Currency.AUD)
    USD_CHF = (Currency.USD, Currency.CHF)
    EUR_CAD = (Currency.EUR, Currency.CAD)
    GBP_AUD = (Currency.GBP, Currency.AUD)
    CHF_JPY = (Currency.CHF, Currency.JPY)
    AUD_CHF = (Currency.AUD, Currency.CHF)
    CAD_CHF = (Currency.CAD, Currency.CHF)
    EUR_CHF = (Currency.EUR, Currency.CHF)
    GBP_CHF = (Currency.GBP, Currency.CHF)
    AUD_GBP = (Currency.AUD, Currency.GBP)
    CAD_AUD = (Currency.CAD, Currency.AUD)
    JPY_CAD = (Currency.JPY, Currency.CAD)
    JPY_AUD = (Currency.JPY, Currency.AUD)
    JPY_GBP = (Currency.JPY, Currency.GBP)
    CHF_CAD = (Currency.CHF, Currency.CAD)
    CHF_AUD = (Currency.CHF, Currency.AUD)
    CHF_GBP = (Currency.CHF, Currency.GBP)
    CAD_GBP = (Currency.CAD, Currency.GBP)
    AUD_EUR = (Currency.AUD, Currency.EUR)
    CAD_EUR = (Currency.CAD, Currency.EUR)
    JPY_EUR = (Currency.JPY, Currency.EUR)
    CHF_EUR = (Currency.CHF, Currency.EUR)

    @classmethod
    def from_string(cls, *args):
        if len(args) == 1:  # Single string argument
            pair_str = args[0]
            if len(pair_str) == 7 and pair_str[3] == '/':  # Format: "XXX/YYY"
                first_currency = Currency[pair_str[:3]]
                second_currency = Currency[pair_str[4:]]
            elif len(pair_str) == 6:  # Format: "XXXYYY"
                first_currency = Currency[pair_str[:3]]
                second_currency = Currency[pair_str[3:]]
            else:
                raise ValueError("Invalid string format for currency pair.")
        elif len(args) == 2:  # Two separate currency arguments
            first_currency, second_currency = args
            if isinstance(first_currency, str):
                first_currency = Currency[first_currency]
            elif not isinstance(first_currency, Currency):
                raise ValueError("First argument must be an instance of Currency or a valid currency string.")
            
            if isinstance(second_currency, str):
                second_currency = Currency[second_currency]
            elif not isinstance(second_currency, Currency):
                raise ValueError("Second argument must be an instance of Currency or a valid currency string.")
        else:
            raise ValueError("Invalid number of arguments for CurrencyPair constructor.")

        # Find the matching CurrencyPair (direct or inverted)
        for pair in cls:
            if pair.value == (first_currency, second_currency):
                return pair
            if pair.value == (second_currency, first_currency):  # Check for inverted pair
                return pair

        raise ValueError(f"No matching CurrencyPair found for {first_currency}/{second_currency}.")
    
    def get_domestic_currency(self):
        """Returns the domestic currency of the currency pair."""
        return self.value[1]

    def get_foreign_currency(self):
        """Returns the foreign currency of the currency pair."""
        return self.value[0]

    def __str__(self):
        foreign, domestic = self.value
        return f"{foreign.value}/{domestic.value}"
