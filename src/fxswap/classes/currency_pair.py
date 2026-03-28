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
                base_currency = Currency[pair_str[:3]]
                quote_currency = Currency[pair_str[4:]]
            elif len(pair_str) == 6:  # Format: "XXXYYY"
                base_currency = Currency[pair_str[:3]]
                quote_currency = Currency[pair_str[3:]]
            else:
                raise ValueError("Invalid string format for currency pair.")
        elif len(args) == 2:  # Two separate currency arguments
            base_currency, quote_currency = args
            if isinstance(base_currency, str):
                base_currency = Currency[base_currency]
            elif not isinstance(base_currency, Currency):
                raise ValueError("First argument must be an instance of Currency or a valid currency string.")

            if isinstance(quote_currency, str):
                quote_currency = Currency[quote_currency]
            elif not isinstance(quote_currency, Currency):
                raise ValueError("Second argument must be an instance of Currency or a valid currency string.")
        else:
            raise ValueError("Invalid number of arguments for CurrencyPair constructor.")

        # Find the matching CurrencyPair (direct or inverted)
        for pair in cls:
            if pair.value == (base_currency, quote_currency):
                return pair
            if pair.value == (quote_currency, base_currency):  # Check for inverted pair
                return pair

        raise ValueError(f"No matching CurrencyPair found for {base_currency}/{quote_currency}.")

    def get_base_currency(self):
        """Returns the base currency of the currency pair."""
        return self.value[0]

    def get_quote_currency(self):
        """Returns the quote currency of the currency pair."""
        return self.value[1]

    def __str__(self):
        base, quote = self.value
        return f"{base.value}/{quote.value}"
