from .FXTrade import FXTrade  # Ensure FXTrade is imported
from .direction import Direction  # Ensure Direction is imported

class FXSwap:
    def __init__(self, fx_trade_near: FXTrade, fx_trade_far: FXTrade):
        if not isinstance(fx_trade_near, FXTrade) or not isinstance(fx_trade_far, FXTrade):
            raise TypeError("Both fx_trade_near and fx_trade_far must be instances of FXTrade")
        if fx_trade_near.direction == fx_trade_far.direction:
            raise ValueError("FXSwap trades must have opposite directions")
        if fx_trade_near.payment_receive.date == fx_trade_far.payment_receive.date:
            raise ValueError("FXSwap trades must have different payment dates")
        self.fx_trade_near = fx_trade_near
        self.fx_trade_far = fx_trade_far
        self.direction = Direction.BUY_SELL if fx_trade_near.direction == Direction.BUY else Direction.SELL_BUY

    @property
    def price(self):
        """Calculate the swap price as the difference between far leg and near leg trade prices."""
        return self.fx_trade_far.price - self.fx_trade_near.price

    def __repr__(self):
        return (f"FXSwap(near_leg={self.fx_trade_near}, far_leg={self.fx_trade_far}, direction={self.direction.value})")