from abc import ABC, abstractmethod
from . import mm_enums


class BaseInstrument:
    def ___init__(self, symbol: str, maker_fee: float, taker_fee: float):
        self.symbol = symbol
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
    
        
    @property
    def name(self) -> str:
        return self.symbol
    
    
    @abstractmethod
    def equity(self, mid: float, balance: float, position: float, avg_price: float) -> float:
        return balance + self.pnl(position, avg_price, mid)
        
        
    @abstractmethod
    def get_qty_from_notional(self, price: float, notional: float) -> float:
        return notional / price
    
    
    @abstractmethod
    def pnl(self, qty: float, entry_price: float, exit_price: float) -> float:
        pass
    
    
    @abstractmethod
    def fees(self, qty: float, fill_type: mm_enums.FillType) -> float:
        if fill_type == mm_enums.FillType.MAKER:
            return abs(qty) * self.maker_fee
        else:
            return abs(qty) * self.taker_fee