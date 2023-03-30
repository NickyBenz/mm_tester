import math
import numpy as np
import pandas as pd
from typing import List, Tuple
from . import base_quoter, base_instrument, order, exchange


class ASQuoter(base_quoter.BaseQuoter):
    def __init__(self, instr: base_instrument.BaseInstrument, inventory: float, gamma: float, kappa: float, tau: float, 
                 volatility: float, price_skew: float, size_skew: float, 
                 tick_size: float, lot_size: float, max_quote_size: float):
        super().__init__({"q": inventory, "gamma": gamma, "kappa": kappa,  "tau": tau, "sigma": volatility, 
                          "price_skew_factor": price_skew, "size_skew_factor": size_skew, 
                          "tick_multiplier": 1.0 / tick_size, "lot_size": lot_size, "quote_size": max_quote_size})
        self.instrument = instr
    
    
    def quote(self, timestamp: pd.DatetimeIndex, strategy: exchange.BaseStrategy, 
              mid_price: float, levels: float)-> Tuple[List[order.Order], List[order.Order]]:
        reserve_price = mid_price - self.q * self.gamma * (self.sigma**2) * self.tau
        spread = self.gamma * (self.sigma**2) * self.tau + (2.0 / self.gamma) * math.log(1 + self.gamma / self.kappa)
        return self.compute(timestamp, strategy, reserve_price, levels, spread)
        
    def compute(self, timestamp: pd.DatetimeIndex, strategy: exchange.BaseStrategy,
                reserve_price: float, levels: int, spread: float)-> Tuple[List[order.Order], List[order.Order]]:
        weights = np.exp(np.linspace(0, 1, levels)) * self.size_skew_factor
        normalized_weights = weights / np.sum(weights)
        sizes = (self.quote_size * normalized_weights).round()
        spreads = np.power(self.price_skew_factor, np.linspace(0, levels-1, levels)) * spread
        bid_prices = np.round((reserve_price - spreads) * self.tick_multiplier) / self.tick_multiplier
        ask_prices = np.round((reserve_price + spreads) * self.tick_multiplier) / self.tick_multiplier
        bid_sizes = self.instrument.get_qty_from_notional(bid_prices, sizes)
        ask_sizes = self.instrument.get_qty_from_notional(ask_prices, sizes)
        
        bids = []
        asks = []
        for i in range(levels):
            bids.append(order.Order(timestamp, strategy, self.instrument, bid_prices[i], bid_sizes[i]))
            asks.append(order.Order(timestamp, strategy, self.instrument, ask_prices[i], ask_sizes[i]))
        
        return (bids, asks)