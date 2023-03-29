import pandas as pd
from . import base_instrument

class Record:
    def __init__(self, counter: int, timestamp: pd.DatetimeIndex, series: pd.Series):
        self.counter: int = counter
        self.timestamp: pd.DatetimeIndex = timestamp
        self.series: pd.Series = series
    
    
    def get_instrument_data(self, instrument: base_instrument.BaseInstrument, key: str) -> any:
        lookup = instrument.name + "_" + key
        return self.series[lookup]
    
    
    def get(self, key: str) -> any:
        return self.series[key]
    
    
    def get_all(self) -> pd.Series:
        return self.series
    
