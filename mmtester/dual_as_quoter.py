import math
import numpy as np
import pandas as pd
from typing import List, Tuple
from mmtester import base_instrument, order, exchange, mm_enums


class DualASQuoter():
    def __init__(self, spot_instr: base_instrument.BaseInstrument, future_instr: base_instrument.BaseInstrument,
                 future_q: float, spot_q: float, gamma: float, kappa: float, tau: float, volatility: float, 
                 spot_bid_price_skew: float, spot_ask_price_skew: float,
                 spot_bid_size_skew: float, spot_ask_size_skew: float,
                 future_bid_price_skew: float, future_ask_price_skew: float,
                 future_bid_size_skew: float, future_ask_size_skew: float,
                 spot_bid_levels: float, spot_ask_levels: float,
                 future_bid_levels: float, future_ask_levels: float,
                 spot_q_skew: float, future_q_skew: float,
                 tick_size: float, lot_size: float, max_quote_size: float):
        self.spot_q=spot_q
        self.future_q = future_q
        self.gamma=gamma
        self.kappa=kappa
        self.tau=tau
        self.sigma=volatility 
        self.spot_bid_price_skew_factor=spot_bid_price_skew 
        self.spot_ask_price_skew_factor=spot_ask_price_skew
        self.spot_bid_size_skew_factor=spot_bid_size_skew
        self.spot_ask_size_skew_factor=spot_ask_size_skew
        self.future_bid_price_skew_factor=future_bid_price_skew
        self.future_ask_price_skew_factor=future_ask_price_skew
        self.future_bid_size_skew_factor=future_bid_size_skew
        self.future_ask_size_skew_factor=future_ask_size_skew
        self.spot_bid_levels = spot_bid_levels
        self.spot_ask_levels = spot_ask_levels
        self.future_bid_levels = future_bid_levels
        self.future_ask_levels = future_ask_levels
        self.spot_q_skew = spot_q_skew
        self.future_q_skew = future_q_skew
        self.tick_multiplier = 1.0 / tick_size 
        self.lot_size=lot_size
        self.quote_size=max_quote_size
        self.spot_instr = spot_instr
        self.future_instr = future_instr
    

    def quote(self, timestamp: pd.DatetimeIndex, strategy: exchange.BaseStrategy, 
              spot_price: float, future_price: float)-> Tuple[List[order.Order], List[order.Order]]:
        spot_reserve_price = spot_price - self.spot_q_skew * self.spot_q * self.gamma * spot_price * (self.sigma**2) * self.tau
        future_reserve_price = future_price - self.future_q_skew * self.future_q * self.gamma * future_price * (self.sigma**2) * self.tau
        spread = self.gamma * (self.sigma**2) * self.tau + (2.0 / self.gamma) * math.log(1 + self.gamma / self.kappa)
        return self.compute(timestamp, strategy, spot_reserve_price, future_reserve_price, spread * 0.5)

        
    def compute(self, timestamp: pd.DatetimeIndex, strategy: exchange.BaseStrategy,
                spot_reserve_price: float, future_reserve_price: float,  
                spread: float)-> Tuple[List[order.Order], List[order.Order], List[order.Order], List[order.Order]]:
        spot_bid_size_weights = np.arange(1, self.spot_bid_levels + 1, 1)
        spot_ask_size_weights = np.arange(1, self.spot_ask_levels + 1, 1)
        future_bid_size_weights = np.arange(1, self.future_bid_levels + 1, 1)
        future_ask_size_weights = np.arange(1, self.future_ask_levels + 1, 1)
        spot_bid_size_weights = np.power(self.spot_bid_size_skew_factor * 1.0, spot_bid_size_weights)
        spot_ask_size_weights = np.power(self.spot_ask_size_skew_factor * 1.0, spot_ask_size_weights)
        future_bid_size_weights = np.power(self.future_bid_size_skew_factor * 1.0, future_bid_size_weights)
        future_ask_size_weights = np.power(self.future_ask_size_skew_factor * 1.0, future_ask_size_weights)
        
        spot_bid_size_weights /= np.sum(spot_bid_size_weights)
        spot_ask_size_weights /= np.sum(spot_ask_size_weights)
        future_bid_size_weights /= np.sum(future_bid_size_weights)
        future_ask_size_weights /= np.sum(future_ask_size_weights)
        
        spot_bid_size_weights *= self.quote_size 
        spot_ask_size_weights *= self.quote_size 
        future_bid_size_weights *= self.quote_size
        future_ask_size_weights *= self.quote_size
        
        spot_bid_spreads = np.power(self.spot_bid_price_skew_factor, np.linspace(0, self.spot_bid_levels-1, self.spot_bid_levels))
        spot_ask_spreads = np.power(self.spot_ask_price_skew_factor, np.linspace(0, self.spot_ask_levels-1, self.spot_ask_levels))
        future_bid_spreads = np.power(self.future_bid_price_skew_factor, np.linspace(0, self.future_bid_levels-1, self.future_bid_levels))
        future_ask_spreads = np.power(self.future_ask_price_skew_factor, np.linspace(0, self.future_ask_levels-1, self.future_ask_levels))
        spot_bid_prices = np.round((spot_reserve_price - spot_bid_spreads * spread) * self.tick_multiplier) / self.tick_multiplier
        spot_ask_prices = np.round((spot_reserve_price + spot_ask_spreads * spread) * self.tick_multiplier) / self.tick_multiplier
        future_bid_prices = np.round((future_reserve_price - future_bid_spreads * spread) * self.tick_multiplier) / self.tick_multiplier
        future_ask_prices = np.round((future_reserve_price + future_ask_spreads * spread) * self.tick_multiplier) / self.tick_multiplier

        
        spot_bids = []
        spot_asks = []
        future_bids = []
        future_asks = []
        
        for i in range(self.spot_bid_levels):
            spot_bids.append(order.Order(timestamp, strategy.name, self.spot_instr, 
                                         mm_enums.Side.BUY, spot_bid_prices[i], spot_bid_size_weights[i]))
            
        for i in range(self.spot_ask_levels):
            spot_asks.append(order.Order(timestamp, strategy.name, self.spot_instr, 
                                         mm_enums.Side.SELL, spot_ask_prices[i], spot_ask_size_weights[i]))
        
        for i in range(self.future_bid_levels):
            future_bids.append(order.Order(timestamp, strategy.name, self.future_instr, 
                                         mm_enums.Side.BUY, future_bid_prices[i], future_bid_size_weights[i]))
        
        for i in range(self.future_ask_levels):                
            future_asks.append(order.Order(timestamp, strategy.name, self.future_instr, 
                                         mm_enums.Side.SELL, future_ask_prices[i], future_ask_size_weights[i]))
        
        return (spot_bids, spot_asks, future_bids, future_asks)