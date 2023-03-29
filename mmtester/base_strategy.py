from abc import ABC, abstractmethod
from . import mm_enums, exchange, record, order

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.exchange = None
    
    
    @abstractmethod
    def on_exchange_init(self, exchange: exchange.Exchange):
        self.exchange = exchange
    
       
    @abstractmethod
    def on_tick(self, record: record.Record):
        raise RuntimeError("abstraact method")
    
        
    @abstractmethod 
    def on_cancel(self, order: order.Order):
        raise RuntimeError("abstract method")
    
    
    @abstractmethod
    def on_fill(self, order: order.Order, fill_type: mm_enums.FillType):
        raise RuntimeError("abstract method")
        
    