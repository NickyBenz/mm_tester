from abc import ABC, abstractmethod
from . import mm_enums

class BaseStrategy(ABC):
    def __init__(self, name):
        self.name = name
        self.exchange = None
    
    
    @abstractmethod
    def on_exchange_init(self, exchange):
        self.exchange = exchange
    
       
    @abstractmethod
    def on_tick(self, data):
        pass
    
        
    @abstractmethod 
    def on_cancel(self, order):
        pass
    
    
    @abstractmethod
    def on_fill(self, order, state):
        pass
        
    