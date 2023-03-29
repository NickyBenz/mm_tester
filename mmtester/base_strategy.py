from abc import ABC, abstractmethod
from . import mm_enums

class BaseStrategy(ABC):
    def __init__(self, balance):
        self.equity = 0
        self.pnl = 0
        self.fees = 0
        self.initial_balance = balance
        self.balance = balance
        self.positions = {}
    
    
    @abstractmethod
    def on_exchange_init(self):
        pass
    
       
    @abstractmethod
    def on_tick(self, data):
        pass
    
        
    @abstractmethod 
    def on_cancel(self, order):
        pass
    
    
    @abstractmethod
    def on_fill(self, order, state):
        pass
        
    