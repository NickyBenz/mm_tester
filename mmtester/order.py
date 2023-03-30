import pandas as pd
from . import mm_enums, base_instrument


class Order:
    def __init__(self, timestamp: pd.DatetimeIndex, strategy_name: str, 
                 instrument: base_instrument.BaseInstrument,  price: float, quantity:float):
        self.timestamp: pd.DatetimeIndex = timestamp
        self.strategy_name: str = strategy_name
        self.instrument: base_instrument.BaseInstrument = instrument
        self.price: float = price
        self.quantity: float = quantity
        self.state: mm_enums.OrderState = mm_enums.OrderState.NEW