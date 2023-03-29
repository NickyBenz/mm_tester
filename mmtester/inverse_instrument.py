from . import base_instrument


class InverseInstrument(base_instrument.BaseInstrument):
    def __init__(self, symbol) -> None:
        super().__init__(symbol)
        
        
    def  get_qty_from_notional(self, price, notional):
        return super().get_qty_from_notional(price, notional)
    
    
    def pnl(self, qty, entry_price, exit_price):
        return qty * (1.0 - entry_price / exit_price)
    
    
    def equity(self, mid, balance, position, avg_price):
        return super().equity(mid, balance, position, avg_price)
    
    
    def fees(self, qty, fill_type):
        return super().fees(qty, fill_type)
    
        