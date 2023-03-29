from . import base_instrument, mm_enums


class InverseInstrument(base_instrument.BaseInstrument):
    def __init__(self, symbol:str):
        super().__init__(symbol)
        
        
    def  get_qty_from_notional(self, price: float, notional: float) -> float:
        return super().get_qty_from_notional(price, notional)
    
    
    def pnl(self, qty: float, entry_price: float, exit_price: float) -> float:
        return qty * (1.0 - entry_price / exit_price)
    
    
    def equity(self, mid:float, balance: float, position: float, avg_price: float) -> float:
        return super().equity(mid, balance, position, avg_price)
    
    
    def fees(self, qty: float, fill_type: mm_enums.FillType) -> float:
        return super().fees(qty, fill_type)
    
        