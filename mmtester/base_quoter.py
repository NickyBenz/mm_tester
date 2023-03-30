import pandas as pd

from abc import ABC, abstractclassmethod
from typing import List, Tuple
from . import order, exchange


class BaseQuoter(ABC):
    def __init__(self, **kw):
        for name in kw:
            setattr(self, name, kw[name])
            
    @abstractclassmethod
    def quote(self, timestamp: pd.DatetimeIndex, strategy: exchange.BaseStrategy, 
              levels: int, mid_price: float) -> Tuple[List[order.Order], List[order.Order]]:
        pass