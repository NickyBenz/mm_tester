from typing import List, Tuple
from . import base_quoter, order


class ASQuoter(base_quoter.BaseQuoter):
    def __init__(self, inventory: float, gamma: float, kappa: float, tau: float, 
                 volatility: float, price_skew: float, size_skew: float, 
                 tick_size: float, lot_size: float):
        super().__init__({"q": inventory, "gamma": gamma, "kappa": kappa,  "tau": tau, "sigma": volatility, 
                          "price_skew_factor": price_skew, "size_skew_factor": size_skew, 
                          "tick_size": tick_size, "lot_size": lot_size})
    
    
    def quote(self, mid_price: float, levels: float)-> Tuple(List(order.Order), List(order.Order)):
        spread = mid_price * 0.01
        return self.compute(mid_price, levels, spread)
        
    def compute(self, levels: int, mid_price: float, spread: float)-> Tuple(List(order.Order), List(order.Order)):
        return ([][])