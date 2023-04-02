from typing import List
from mmtester import exchange, mm_enums, exchange, order, position, base_instrument, record, base_quoter
import pandas as pd

class SingleMMStrategy(exchange.BaseStrategy):
    def __init__(self, name: str, quoter: base_quoter.BaseQuoter, balance: float, 
                 instrument: base_instrument.BaseInstrument, 
                 total_time_in_seconds: float, levels: int, quote_frequency: int, length: int):
        super().__init__(name)
        self.instrument = instrument
        self.quoter: base_quoter.BaseQuoter = quoter
        self.total_time: float = total_time_in_seconds
        self.levels: int = levels
        self.frequency: int = quote_frequency
        self.position: position.Position = position.Position(balance, instrument, length)
        self.requote: bool = True
        self.curr_step = 0


    def on_cancel(self, order: order.Order):
        pass
    
    
    def on_exchange_init(self, exchange: exchange.Exchange, data_frequency: float):
        return super().on_exchange_init(exchange, data_frequency)
    
    
    def on_fill(self, order: order.Order, fill_type: mm_enums.FillType):
        self.position.on_fill(order, fill_type)
        self.requote = True
    
    
    def on_tick(self, record: record.Record):
        if record is not None:
            if record.counter > 0 and (record.counter  % self.frequency == 0 or self.requote):
                self.exchange.cancel_all(record.timestamp, self.name)
                self.quoter.q = self.position.total_qty / self.position.initial_balance
                self.quoter.tau = ((self.curr_step * self.frequency * self.data_frequency) % (self.total_time * 1000)) 
                self.quoter.tau /= (self.total_time * 1000)
                self.quoter.tau = 1 - self.quoter.tau
                (bids, asks) = self.quoter.quote(record.timestamp, self, 
                                                 record.get_instrument_data(self.instrument, "mid"), self.levels)
                self.exchange.add_quotes(bids, asks)
                self.requote = False
            self.position.record(record)
            self.curr_step += 1