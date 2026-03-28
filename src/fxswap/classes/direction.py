from enum import Enum

class TradeDirection(Enum):  # Renamed from Direction to TradeDirection
    BUY = "BUY"
    SELL = "SELL"
    BUY_SELL = "BUY_SELL"
    SELL_BUY = "SELL_BUY"
    # B = "BUY"  # Added shorthand for BUY
    # S = "SELL"  # Added shorthand for SELL
    # BS = "BUY_SELL"  # Added shorthand for BUY_SELL
    # SB = "SELL_BUY"  # Added shorthand for SELL_BUY
    
    @staticmethod
    def opposite(direction):
        if direction == TradeDirection.BUY:
            return TradeDirection.SELL
        elif direction == TradeDirection.SELL:
            return TradeDirection.BUY
        elif direction == TradeDirection.BUY_SELL:
            return TradeDirection.SELL_BUY
        elif direction == TradeDirection.SELL_BUY:
            return TradeDirection.BUY_SELL
        # elif direction == TradeDirection.B:
        #     return TradeDirection.S
        # elif direction == TradeDirection.S:
        #     return TradeDirection.B
        # elif direction == TradeDirection.BS:
        #     return TradeDirection.SB
        # elif direction == TradeDirection.SB:
        #     return TradeDirection.BS
        else:
            raise ValueError(f"Unknown direction: {direction}")    

class PaymentDirection(Enum):  # Updated enum class for payment direction
    PAY = "PAY"
    RECEIVE = "RECEIVE"
    BUY = "RECEIVE"  # Updated to map BUY to RECEIVE
    SELL = "PAY"  # Updated to map SELL to PAY
    B = "RECEIVE"  # Updated to map B to RECEIVE
    S = "PAY"  # Updated to map S to PAY
    
    def __str__(self):
        return self.value
