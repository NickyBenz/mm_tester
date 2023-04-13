import numpy as np
import pandas as pd
from mmtester.dual_as_quoter import DualASQuoter
from mmtester.exchange import Exchange
from mmtester.multi_mm_strategy import MultiMMStrategy
from mmtester.inverse_instrument import InverseInstrument
from mmtester.data import Data
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    counter = 1
    perp_res = pd.DataFrame(columns=['days', 'balance', 'sharpe', 'sortino', 'return', 'fee', 'drawdown', 'num_trades', 'q_trades'])
    future_res = pd.DataFrame(columns=['days', 'balance', 'sharpe', 'sortino', 'return', 'fee', 'drawdown', 'num_trades', 'q_trades'])
    
    target_spot = 1
    target_future = -1
    init_spot_qty = 0
    init_future_qty = 0
    init_spot_avg_price = 0
    init_future_avg_price = 0
    
    for df in pd.read_csv("./mmtester/data_generator/data/data.csv.gz", header=0, index_col=0, parse_dates=[0], chunksize=9000):
        exch = Exchange(500, 500)
        spot_instr = InverseInstrument("perp", 0.000, 0.0005)
        future_instr = InverseInstrument("future", -0.0001, 0.0005)
        quoter = DualASQuoter(spot_instr=spot_instr,
                          future_instr=future_instr,
                          future_q=0, 
                          spot_q=0, 
                          gamma=0.5, 
                          kappa=2, 
                          tau=1, 
                          volatility=0.2,
                          spot_bid_price_skew=3,
                          spot_ask_price_skew=3,
                          spot_bid_size_skew=1,
                          spot_ask_size_skew=1,
                          future_bid_price_skew=3,
                          future_ask_price_skew=3,
                          future_bid_size_skew=1,
                          future_ask_size_skew=1,
                          spot_bid_levels=5,
                          spot_ask_levels=5,
                          future_bid_levels=5,
                          future_ask_levels=5,
                          spot_target_pct=target_spot,
                          future_target_pct=target_future,
                          tick_size=0.05,
                          lot_size=0.001,
                          max_quote_size=2)
        
        target_spot *= -1
        target_future *= -1
        
        strategy = MultiMMStrategy("test_strategy", quoter, 2, 1, 
                                   init_spot_qty, init_spot_avg_price, 
                                   init_future_qty, init_future_avg_price,
                                   spot_instr, future_instr, 1200, 2000, df.shape[0])
        exch.register(strategy)
        exch.start(Data(df, 100))
    
        iter = 0
        while exch.step():
            iter += 1
        
        init_spot_qty = strategy.spot_position.total_qty
        init_spot_avg_price = strategy.spot_position.avg_price
        init_future_qty = strategy.future_position.total_qty
        init_future_avg_price = strategy.future_position.avg_price
        
        backtest_days, balance, sr, sortino, pret, fee, draw, ftn, ftq = strategy.spot_position.stat.summary("perp" + str(counter))
        perp_res = perp_res.append({'days':backtest_days, 'balance':balance, 
                                    'sharpe':sr, 'sortino':sortino, 'return': pret,
                                    'fee': fee, 'drawdown': draw, 
                                    'num_trades': ftn, 'q_trades': ftq}, ignore_index=True)
        backtest_days, balance, sr, sortino, fret, fee, draw, ftn, ftq = strategy.future_position.stat.summary("future" + str(counter))
        future_res = future_res.append({'days':backtest_days, 'balance':balance, 
                                        'sharpe':sr, 'sortino':sortino, 'return': fret,
                                        'fee': fee, 'drawdown': draw, 
                                        'num_trades': ftn, 'q_trades': ftq}, ignore_index=True)
        
        print("Counter=", counter, pret+fret, pret, fret)
        counter += 1

    perp_res.to_csv("perp.csv", header=True)
    future_res.to_csv("future.csv", header=True)