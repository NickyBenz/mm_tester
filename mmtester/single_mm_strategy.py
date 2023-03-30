from typing import List
from mmtester import exchange, mm_enums, exchange, order, position, base_instrument, record, base_quoter


class SingleMMStrategy(exchange.BaseStrategy):
    def __init__(self, name: str, quoter: base_quoter.BaseQuoter, balance: float, 
                 instrument: base_instrument.BaseInstrument, 
                 total_time: float, levels: int, quote_frequency: int):
        super().__init__(name)
        self.instrument = instrument
        self.quoter: base_quoter.BaseQuoter = quoter
        self.total_time: float = total_time
        self.levels: int = levels
        self.frequency: int = quote_frequency
        self.position: position.Position = position.Position(balance, instrument)
        self.requote: bool = True


    def on_cancel(self, order: order.Order):
        pass
    
    
    def on_exchange_init(self, exchange: exchange.Exchange):
        return super().on_exchange_init(exchange)
    
    
    def on_fill(self, order: order.Order, fill_type: mm_enums.FillType):
        self.position.on_fill(order, fill_type)
        self.requote = True
    
    
    def on_tick(self, record: record.Record):
        if record.counter > 0 and record.counter  % self.frequency == 0 and self.requote:
            self.exchange.cancel_all(record.timestamp, self)
            (bids, asks) = self.quoter.quote(record.timestamp, self, self.levels, record.get_instrument_data(self.instrument, "mid"))
            self.exchange.add_quotes(bids, asks)
            self.requote = False
        self.position.record(record)