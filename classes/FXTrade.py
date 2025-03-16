from .currency import Currency
from .direction import PaymentDirection, TradeDirection
from .currency_pair import CurrencyPair
from .payment import Payment
from datetime import date

class FXTrade:
    def __init__(
        self,
        currency_pair: CurrencyPair | tuple[str, str] | str,
        giv_amount: float,
        value_date: date,
        giv_direction: TradeDirection,
        rate: float = None,
        alt_amount: float = None,
        giv_currency: str = None,
        trade_date: date = None,
        done: bool = False
    ):
        # Normalize currency_pair to CurrencyPair instance
        if isinstance(currency_pair, str):
            currency_pair = CurrencyPair(tuple(currency_pair.split("/")))
        elif isinstance(currency_pair, tuple):
            currency_pair = CurrencyPair(currency_pair)
            
        self.currency_pair = currency_pair
        self.foreign_currency = self.currency_pair.get_foreign_currency()
        self.domestic_currency = self.currency_pair.get_domestic_currency()
        self.giv_currency = giv_currency or self.foreign_currency  # Default to foreign currency

        # Validate giv_currency
        if self.giv_currency not in currency_pair.value:
            raise ValueError("giv_currency must match one of the currencies in the currency pair.")

        # Assign mandatory parameters
        self.giv_amount = giv_amount
        self.trade_date = trade_date or date.today()  # Default to today if not provided
        self.alt_currency = self.domestic_currency if self.giv_currency == self.foreign_currency else self.foreign_currency
        self.giv_direction = giv_direction
        self.alt_direction = TradeDirection.opposite(self.giv_direction)        
        self.direction = self.giv_direction if self.giv_currency == self.foreign_currency else self.alt_direction
        self.foreign_direction = self.direction
        self.domestic_direction = TradeDirection.opposite(self.direction)
        self.done = done
        
        # Assign optional parameters
        self.rate = rate
        self.alt_amount = alt_amount
        
        # Create synthetic payments based on the provided fields
        if self.giv_direction == TradeDirection.BUY:
            self.giv_payment = Payment(value_date, self.giv_currency, self.giv_amount, PaymentDirection.RECEIVE)
            self.alt_payment = Payment(value_date, self.alt_currency, self.alt_amount, PaymentDirection.PAY)
        elif self.giv_direction == TradeDirection.SELL:
            self.giv_payment = Payment(value_date, self.giv_currency, self.giv_amount, PaymentDirection.PAY)
            self.alt_payment = Payment(value_date, self.alt_currency, self.alt_amount, PaymentDirection.RECEIVE)

    # def set_rate(self, rate: float):
    #     """Set the rate and update alt_amount accordingly."""
    #     if rate <= 0:
    #         raise ValueError("Rate must be a positive number.")
    #     self.rate = rate


    def __repr__(self):
        return (
            f"FXTrade(\n"
            f"    trade_date={self.trade_date},\n"
            f"    currency_pair={str(self.currency_pair)},\n"
            f"    giv_amount={self.giv_amount},\n"
            f"    rate={self.rate},\n"
            f"    alt_amount={self.alt_amount},\n"
            f"    giv_currency={self.giv_currency},\n"
            f"    alt_currency={self.alt_currency},\n"
            f"    giv_direction={self.giv_direction.value},\n"
            f"    alt_direction={self.alt_direction.value},\n"
            f"    direction={self.direction.value},\n"
            f"    foreign_currency={self.foreign_currency},\n"
            f"    foreign_direction={self.foreign_direction.value},\n"
            f"    domestic_currency={self.domestic_currency},\n"
            f"    domestic_direction={self.domestic_direction.value},\n"
            f"    giv_payment={self.giv_payment},\n"
            f"    alt_payment={self.alt_payment},\n"
            f"    done={self.done}\n"
            f")"
        )