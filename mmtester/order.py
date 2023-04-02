import pandas as pd
from mmtester import mm_enums, base_instrument


class Order:
    def __init__(self, timestamp: pd.DatetimeIndex, strategy_name: str, 
                 instrument: base_instrument.BaseInstrument,  side: mm_enums.Side, 
                 price: float, quantity:float):
        self.timestamp: pd.DatetimeIndex = timestamp
        self.strategy_name: str = strategy_name
        self.instrument: base_instrument.BaseInstrument = instrument
        self.side = side
        self.price: float = price
        self.quantity: float = quantity
        self.state: mm_enums.OrderState = mm_enums.OrderState.NEW