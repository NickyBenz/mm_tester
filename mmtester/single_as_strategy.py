from . import base_strategy, mm_enums, exchange, order, position

class SingleASstrategy(base_strategy.BaseStrategy):
    def __init__(self, name, balance, instrument, total_time):
        super().__init__(name)
        self.total_time = total_time
        self.position = position.Position(balance, instrument)


    def on_cancel(self, order):
        return super().on_cancel(order)
    
    
    def on_exchange_init(self):
        return super().on_exchange_init()
    
    
    def on_fill(self, order, state):
        return super().on_fill(order, state)
    
    
    def on_tick(self, record):
        self.position.record(record)