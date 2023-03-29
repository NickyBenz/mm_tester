import math
import numpy as np
import pandas as pd
from typing import List, Set, Dict
from . import mm_enums, data, base_strategy, order, record

class Exchange:
    def __init__(self, market_data_latency_ms: float, order_fill_latency_ms: float):
        self.curr_step: int = 0
        self.market_data_latency: float = market_data_latency_ms
        self.order_fill_latency: float = order_fill_latency_ms
        self.strategies: Set(base_strategy.BaseStrategy) = set()

    
    def start(self, dataObject: data.Data):
        self.dataObject: data.Data = dataObject
        self.sample_frequency: float = dataObject.frequency
        self.market_latency_steps: int = int(math.ceil(self.market_dataObject_latency / self.sample_frequency))
        self.curr_step = 0
        self.max_step: int = dataObject.get_rows() - 1
        self.orders: List(order.Order) = []
        self.cancels: Dict(order.Order, pd.DatetimeIndex) = {}
        
        for strategy in self.strategies:
            strategy.on_exchange_init(self) 
    
    
    def close_all(self):
        for order in self.orders:
            assert(order.state == mm_enums.OrderState.NEW)
            order.state = mm_enums.OrderState.FILLED
            order.strategy.on_fill(order, mm_enums.FillType.TAKER)
        self.orders.clear()
        
    
    def cancel_order(self, timestamp: pd.DatetimeIndex, order: order.Order):
        if order.state == mm_enums.OrderState.NEW:
            self.cancels[order] = timestamp
        
        
    def cancel_all(self, timestamp: pd.DatetimeIndex, strategy: base_strategy.BaseStrategy):
        for order in self.orders[:]:
            if order.strategy == strategy:
                self.cancels[order] = timestamp
    
        
    def process_cancels(self):
        cancelled = []
        
        for order in self.cancels:
            if self.cancels[order] + self.market_dataObject_latency >= self.df.index[self.curr_step]:
                if order.state != mm_enums.OrderState.FILLED:
                    order.state = mm_enums.OrderState.CANCELED
                    self.orders.remove(order)
                    order.strategy.on_cancel(order)

                cancelled.append(order)
        
        for order in cancelled:
            del self.cancels[order]
            
            
    def add_quotes(self, bids: List(order), asks: List(order)):
        assert(len(bids) == len(asks))
        
        for i in range(len(bids)):
            self.add_order(bids[i])
            self.add_order(asks[i])
        
        
    def add_order(self, order: order.Order):
        assert(order.state == mm_enums.OrderState.NEW)
        self.orders.append(order)
    
    
    def register(self, strategy: base_strategy.BaseStrategy):
        self.strategies.add(strategy)
        
    
    def get_record(self) -> record.Record:
        if self.curr_step < self.market_latency_steps:
            return None
        
        step = self.curr_step - self.market_latency_steps
        return self.dataObject.get_record(step)


    def fill_orders(self):    
        record = self.dataObject.get_record(self.curr_step)
        
        for order in self.orders[:]:
            assert(order.state == mm_enums.OrderState.NEW)
            if order.timestamp + pd.Timedelta(self.order_fill_latency, unit="milliseconds") >= record.timestamp:
                bid = record.get_instrument_data(order.instrument, "bid")
                ask = record.get_instrument_data(order.intrument, "ask")
                
                if order.side == mm_enums.Side.BUY and order.price > ask:
                    order.state = mm_enums.OrderState.FILLED
                    order.strategy.on_fill(order, mm_enums.FillType.MAKER)
                    self.orders.remove(order)
                elif order.side == mm_enums.Side.SELL and order.price < bid:
                    order.state = mm_enums.OrderState.FILLED
                    order.strategy.on_fill(order, mm_enums.FillType.MAKER)
                    self.orders.remove(order)
        
        
    def step(self) -> bool:
        if self.curr_step >= self.max_step:
            return False
        
        for strategy in self.strategies:
            strategy.on_tick(self.get_data())
        
        self.process_cancels()
        self.fill_orders()
        
        self.curr_step += 1
        return True
