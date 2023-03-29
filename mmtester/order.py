from . import mm_enums


class Order:
    def __init__(self, timestamp, strategy, instrument,  price, quantity):
        self.timestamp = timestamp
        self.strategy = strategy
        self.instrument = instrument
        self.price = price
        self.quantity = quantity
        self.state = mm_enums.OrderState.NEW