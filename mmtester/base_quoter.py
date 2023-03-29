from abc import ABC, abstractclassmethod
from typing import List, Tuple
from . import order


class BaseQuoter(ABC):
    def __init__(self, **kw):
        for name in kw:
            setattr(self, name, kw[name])
            
    @abstractclassmethod
    def quote(self, levels: int, mid_price: float) -> Tuple(List(order.Order), List(order.Order)):
        pass