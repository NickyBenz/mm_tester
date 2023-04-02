import math
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import List, Set, Dict
from mmtester import mm_enums, data, exchange, order, record


class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.exchange = None
        self.data_frequency = 0
    
    
    @abstractmethod
    def on_tick(self, record: record.Record):
        raise RuntimeError("abstraact method")
    
        
    @abstractmethod 
    def on_cancel(self, order: order.Order):
        raise RuntimeError("abstract method")
    
    
    @abstractmethod 
    def on_exchange_init(self, exch, data_frequency):
        self.exchange = exch
        self.data_frequency = data_frequency
        
    
    @abstractmethod
    def on_fill(self, order: order.Order, fill_type: mm_enums.FillType):
        raise RuntimeError("abstract method")
    

class Exchange:
    def __init__(self, market_data_latency_ms: float, order_fill_latency_ms: float):
        self.curr_step: int = 0
        self.market_data_latency: float = market_data_latency_ms
        self.order_fill_latency: float = order_fill_latency_ms
        self.strategies: Dict[str, exchange.BaseStrategy] = {}

    
    def start(self, dataObject: data.Data):
        self.dataObject: data.Data = dataObject
        self.sample_frequency: float = dataObject.frequency
        self.market_latency_steps: int = int(math.ceil(self.market_data_latency / self.sample_frequency))
        self.curr_step = 0
        self.max_step: int = dataObject.get_rows() - 1
        self.orders: List[order.Order] = []
        self.cancels: Dict[order.Order, pd.DatetimeIndex] = {}
        
        for strat  in self.strategies.values():
            strat.on_exchange_init(self, self.dataObject.frequency)
                        
    
    def get_instruments(self):
        return self.data.get_instrument_names()
    
    
    def get_feature_names(self):
        return self.data.get_feature_names()
    
    
    def close_all(self):
        for order in self.orders:
            assert(order.state == mm_enums.OrderState.NEW)
            order.state = mm_enums.OrderState.FILLED
            self.strategies[order.strategy_name].on_fill(order, mm_enums.FillType.TAKER)
        self.orders.clear()
        
    
    def cancel_order(self, timestamp: pd.DatetimeIndex, order: order.Order):
        assert(order.strategy_name in self.strategies)
        if order.state == mm_enums.OrderState.NEW:
            self.cancels[order] = timestamp
        
        
    def cancel_all(self, timestamp: pd.DatetimeIndex, strategy_name: str):
        for order in self.orders[:]:
            if order.strategy_name == strategy_name:
                self.cancels[order] = timestamp
    
        
    def process_cancels(self):
        cancelled = []
        
        for order in self.cancels:
            if self.df.index[self.curr_step] >= self.cancels[order] + pd.Timedelta(self.market_data_latency, unit="milliseconds"):
                if order.state != mm_enums.OrderState.FILLED:
                    order.state = mm_enums.OrderState.CANCELED
                    self.orders.remove(order)
                    self.strategies[order.strategy_name].on_cancel(order)

                cancelled.append(order)
        
        for order in cancelled:
            del self.cancels[order]
            
            
    def add_quotes(self, bids: List[order.Order], asks: List[order.Order]):
        assert(len(bids) == len(asks))
        
        for i in range(len(bids)):
            self.add_order(bids[i])
            self.add_order(asks[i])
        
        
    def add_order(self, order: order.Order):
        assert(order.strategy_name in self.strategies)
        assert(order.state == mm_enums.OrderState.NEW)
        self.orders.append(order)
    
    
    def register(self, strategy: BaseStrategy):
        if not strategy.name in self.strategies:
            self.strategies[strategy.name] = strategy
        
    
    def get_record(self) -> record.Record:
        if self.curr_step < self.market_latency_steps:
            return None
        
        step = self.curr_step - self.market_latency_steps
        return self.dataObject.get_record(self.curr_step, step)


    def fill_orders(self):    
        record = self.dataObject.get_record(self.curr_step, self.curr_step)
        
        for order in self.orders[:]:
            assert(order.state == mm_enums.OrderState.NEW)
            if record.timestamp >= order.timestamp + pd.Timedelta(self.order_fill_latency, unit="milliseconds"):
                bid = record.get_instrument_data(order.instrument, "bid")
                ask = record.get_instrument_data(order.instrument, "ask")
                
                if order.side == mm_enums.Side.BUY and order.price > ask:
                    order.state = mm_enums.OrderState.FILLED
                    self.strategies[order.strategy_name].on_fill(order, mm_enums.FillType.MAKER)
                    self.orders.remove(order)
                elif order.side == mm_enums.Side.SELL and order.price < bid:
                    order.state = mm_enums.OrderState.FILLED
                    self.strategies[order.strategy_name].on_fill(order, mm_enums.FillType.MAKER)
                    self.orders.remove(order)
        
        
    def step(self) -> bool:
        if self.curr_step >= self.max_step:
            self.close_all()
            for strat in self.strategies.values():
                strat.on_tick(self.get_record())
            return False
        
        for strategy in self.strategies.values():
            strategy.on_tick(self.get_record())
        
        self.process_cancels()
        self.fill_orders()
        
        self.curr_step += 1
        return True
