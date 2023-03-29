import math
import numpy as np
import pandas as pd
from . import mm_enums

class Exchange:
    def __init__(self, market_data_latency, order_fill_latency):
        self.curr_step = 0
        self.market_data_latency = market_data_latency
        self.order_fill_latency = order_fill_latency
        self.strategies = {}

    
    def start(self, df, df_sample_freq_milliseconds):
        self.df = df
        self.sample_frequency = df_sample_freq_milliseconds
        self.market_latency_steps = int(math.ceil(self.market_data_latency / self.sample_frequency))
        self.curr_step = 0
        self.max_step = df.shape[0] - 1
        self.orders = []
        self.cancels = {}
        
        for strategy in self.strategies.values():
            strategy.on_exchange_init(self) 
    
    
    def close_all(self):
        for order in self.orders:
            assert(order.state == mm_enums.OrderState.NEW)
            order.state = mm_enums.OrderState.FILLED
            order.strategy.on_fill(order, mm_enums.FillType.TAKER)
        self.orders.clear()
        
    
    def cancel_order(self, timestamp, order):
        if order.state == mm_enums.OrderState.NEW:
            self.cancels[order] = timestamp
        
        
    def cancel_all(self, timestamp, strategy):
        for order in self.orders[:]:
            if order.strategy == strategy:
                self.cancels[order] = timestamp
    
        
    def process_cancels(self):
        cancelled = []
        
        for order in self.cancels:
            if self.cancels[order] + self.market_data_latency >= self.df.index[self.curr_step]:
                if order.state != mm_enums.OrderState.FILLED:
                    order.state = mm_enums.OrderState.CANCELED
                    self.orders.remove(order)
                    order.strategy.on_cancel(order)

                cancelled.append(order)
        
        for order in cancelled:
            del self.cancels[order]
            
                
    def add_order(self, order):
        assert(order.state == mm_enums.OrderState.NEW)
        self.orders.append(order)
    
    
    def register(self, strategy):
        self.strategies[strategy.name] = strategy
        
    
    def get_data(self):
        if self.curr_step < self.market_latency_steps:
            return None
        return self.df.iloc[self.curr_step - self.market_latency_steps, :]


    def fill_orders(self):    
        ts = self.df.index[self.curr_step]
        data = self.df.iloc[self.curr_step, :]
        
        for order in self.orders[:]:
            assert(order.state == mm_enums.OrderState.NEW)
            if order.timestamp + pd.Timedelta(self.order_fill_latency, unit="milliseconds") >= ts:
                bid = data[order.instrument.name + "_bid"]
                ask = data[order.instrument.name + "_ask"]
                
                if order.side == mm_enums.Side.BUY and order.price > ask:
                    order.state = mm_enums.OrderState.FILLED
                    order.strategy.on_fill(order, mm_enums.FillType.MAKER)
                    self.orders.remove(order)
                elif order.side == mm_enums.Side.SELL and order.price < bid:
                    order.state = mm_enums.OrderState.FILLED
                    order.strategy.on_fill(order, mm_enums.FillType.MAKER)
                    self.orders.remove(order)
        
        
    def step(self):
        if self.curr_step >= self.max_step:
            return False
        
        for strategy in self.strategies.values():
            strategy.on_tick(self.get_data())
        
        self.process_cancels()
        self.fill_orders()
        
        self.curr_step += 1
        return True
