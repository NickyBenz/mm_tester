import numpy as np
from . import mm_enums
from . import stat


class Position:
    def __init__(self, balance, instrument):
        self.initial_balance = balance
        self.balance = balance
        self.instrument = instrument
        self.total_qty = 0
        self.fees = 0
        self.trade_num = 0
        self.trade_qty = 0
        self.avg_price = 0
        self.stat = stat.Stat(instrument)
    
    
    def on_fill(self, order, fill_type):
        assert(order.state == mm_enums.OrderState.FILLED)
        qty = order.quantity if order.side == mm_enums.Side.BUY else -order.quantity
        pnl = 0
        
        if self.total_qty == 0:
            self.avg_price = order.price
        elif np.sign(self.total_qty) == np.sign(qty):
            assert(self.avg_price > 0)
            self.avg_price = (abs(qty) * order.price + abs(self.total_qty) * self.avg_price) / abs(qty + self.total_qty)
        else:
            assert(self.avg_price > 0)
            if abs(self.total_qty) == abs(qty):
                pnl += self.instrument.pnl(order.quantity, self.avg_price, order.price)
                self.avg_price = 0
            elif abs(self.total_qty) > abs(qty):
                pnl += self.instrument.pnl(order.quantity, self.avg_price, order.price)
            else:
                pnl = self.instrument.pnl(self.total_qty, self.avg_price, order.price)
                self.avg_price = order.price
                
        self.fees += self.instrument.fees(order.quantity, fill_type)
        self.trade_num += 1
        self.trade_qty += abs(qty)
        self.total_qty += qty
        self.balance += pnl
    
    
    def record(self, record):
        price = record.get_instrument_data(self.instrument, "mid")
        self.stat.record(record.timestamp, price, self.balance, self.total_qty, self.avg_price, self.fees, self.trade_num, self.trade_qty)
    
    