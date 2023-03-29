from . import base_strategy, mm_enums, exchange, order, position

class SingleASstrategy(base_strategy.BaseStrategy):
    def __init__(self, balance, instrument):
        super().__init__(balance)
        self.instrument = instrument


    def on_cancel(self, order):
        return super().on_cancel(order)
    
    
    def on_exchange_init(self):
        return super().on_exchange_init()
    
    
    def on_fill(self, order, state):
        return super().on_fill(order, state)
    
    
    def on_tick(self, data):
        return super().on_tick(data)