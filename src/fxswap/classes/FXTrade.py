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
        self.base_currency = self.currency_pair.get_base_currency()
        self.quote_currency = self.currency_pair.get_quote_currency()
        self.giv_currency = giv_currency or self.base_currency  # Default to base currency

        # Validate giv_currency
        if self.giv_currency not in currency_pair.value:
            raise ValueError("giv_currency must match one of the currencies in the currency pair.")

        # Assign mandatory parameters
        self.giv_amount = giv_amount
        self.trade_date = trade_date or date.today()  # Default to today if not provided
        self.alt_currency = self.quote_currency if self.giv_currency == self.base_currency else self.base_currency
        self.giv_direction = giv_direction
        self.alt_direction = TradeDirection.opposite(self.giv_direction)        
        self.direction = self.giv_direction if self.giv_currency == self.base_currency else self.alt_direction
        self.base_direction = self.direction
        self.quote_direction = TradeDirection.opposite(self.direction)
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

        # Automatically calculate the trade if rate or alt_amount is provided
        if rate is not None or alt_amount is not None:
            self.calculate_trade(rate=rate, alt_amount=alt_amount)
            
    def calculate_trade(self, rate: float = None, alt_amount: float = None):
        """
        Calculate the trade by setting either the rate or the alt_amount.
        If rate is provided, alt_amount is calculated. If alt_amount is provided, rate is calculated.
        """
        # if rate is not None and alt_amount is not None:
        #     raise ValueError("Provide only one of rate or alt_amount, not both.")
        
        if rate is not None:
            if rate <= 0:
                raise ValueError("Rate must be a positive number.")
            self.rate = rate
            if self.giv_currency == self.base_currency:
                self.alt_amount = self.giv_amount * rate    
            elif self.giv_currency == self.quote_currency:
                self.alt_amount = self.giv_amount / rate
            else:
                raise ValueError("giv_currency must be either base or quote currency.")
        elif alt_amount is not None:
            if alt_amount <= 0:
                raise ValueError("alt_amount must be a positive number.")
            self.alt_amount = alt_amount
            if self.giv_currency == self.base_currency:
                self.rate = self.giv_amount/self.alt_amount    
            elif self.giv_currency == self.quote_currency:
                self.rate = self.alt_amount/self.giv_amount
            else:
                raise ValueError("giv_currency must be either base or quote currency.")
        else:
            raise ValueError("Either rate or alt_amount must be provided.")
        
        # Update rate and alt_payment with the calculated
        self.rate = rate
        self.alt_payment.amount = self.alt_amount     

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
            f"    base_currency={self.base_currency},\n"
            f"    base_direction={self.base_direction.value},\n"
            f"    quote_currency={self.quote_currency},\n"
            f"    quote_direction={self.quote_direction.value},\n"
            f"    giv_payment={self.giv_payment},\n"
            f"    alt_payment={self.alt_payment},\n"
            f"    done={self.done}\n"
            f")"
        )
