from typing import List
from mmtester import exchange, mm_enums, exchange, order, position, base_instrument, record, dual_as_quoter
import pandas as pd

class MultiMMStrategy(exchange.BaseStrategy):
    def __init__(self, name: str, quoter: dual_as_quoter.DualASQuoter, spot_balance: float, max_leverage: float, 
                 spot_instr: base_instrument.BaseInstrument, future_instr: base_instrument.BaseInstrument,
                 total_time_in_seconds: float, quote_frequency: int, length: int):
        super().__init__(name)
        self.spot_instr = spot_instr
        self.future_instr = future_instr
        self.quoter: dual_as_quoter.DualASQuoter = quoter
        self.total_time: float = total_time_in_seconds
        self.frequency: int = quote_frequency
        self.max_leverage: float = max_leverage
        self.spot_position: position.Position = position.Position(spot_balance, self.spot_instr, length)
        self.future_position: position.Position = position.Position(spot_balance, self.future_instr, length)
        self.requote: bool = True


    def on_cancel(self, order: order.Order):
        pass
    
    
    def on_exchange_init(self, exchange: exchange.Exchange, data_frequency: float):
        return super().on_exchange_init(exchange, data_frequency)
    
    
    def on_fill(self, order: order.Order, fill_type: mm_enums.FillType):
        if order.instrument == self.spot_instr:
            self.spot_position.on_fill(order, fill_type)
        elif order.instrument == self.future_instr:
            self.future_position.on_fill(order, fill_type)
        else:
            raise RuntimeError("Invalid instrument in fill received")
        self.requote = True
    
    
    def on_tick(self, record: record.Record):
        if record is not None:
            if record.counter > 0 and (record.counter  % self.frequency == 0 or self.requote):
                self.exchange.cancel_all(record.timestamp, self.name)
                self.quoter.delta_q = -1 - self.future_position.total_qty / (self.future_position.initial_balance * self.max_leverage) 
                self.quoter.spot_q = 1 - self.spot_position.total_qty / (self.spot_position.initial_balance * self.max_leverage)
                self.quoter.tau = (record.counter * self.data_frequency) % (self.total_time * 1000)
                self.quoter.tau /= (self.total_time * 1000)
                self.quoter.tau = 1 - self.quoter.tau

                (spot_bids, spot_asks, future_bids, future_asks) = self.quoter.quote(record.timestamp, self, 
                                                                                     record.get_instrument_data(self.spot_instr, "mid"), 
                                                                                     record.get_instrument_data(self.future_instr, "mid"))
                self.exchange.add_quotes(spot_bids, spot_asks)
                self.exchange.add_quotes(future_bids, future_asks)
                self.requote = False
            self.spot_position.record(record)
            self.future_position.record(record)
