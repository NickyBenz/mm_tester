from abc import ABC, abstractmethod
from . import mm_enums


class BaseInstrument:
    def ___init__(self, symbol, maker_fee, taker_fee):
        self.symbol = symbol
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
    
        
    @property
    def name(self):
        return self.symbol
    
    
    @abstractmethod
    def equity(self, mid, balance, position, avg_price):
        return balance + self.pnl(position, avg_price, mid)
        
        
    @abstractmethod
    def get_qty_from_notional(self, price, notional):
        return notional / price
    
    
    @abstractmethod
    def pnl(self, qty, entry_price, exit_price):
        pass
    
    
    @abstractmethod
    def fees(self, qty, fill_type):
        if fill_type == mm_enums.FillType.MAKER:
            return abs(qty) * self.maker_fee
        else:
            return abs(qty) * self.taker_fee
        
    