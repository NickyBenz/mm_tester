import random
import pandas as pd
from mmtester.dual_as_quoter import DualASQuoter
from mmtester.exchange import Exchange
from mmtester.multi_mm_strategy import MultiMMStrategy
from mmtester.inverse_instrument import InverseInstrument
from mmtester.data import Data

if __name__ == '__main__':
    df = pd.read_csv("./mmtester/data_generator/data/data.csv.gz", header=0, index_col=0, parse_dates=[0]).iloc[:36000]
    exch = Exchange(500, 500)
    spot_instr = InverseInstrument("perp", 0.000, 0.0005)
    future_instr = InverseInstrument("future", -0.0001, 0.0005)
    quoter = DualASQuoter(spot_instr=spot_instr,
                          future_instr=future_instr,
                          delta=0, 
                          spot_q=0, 
                          gamma=0.2, 
                          kappa=3, 
                          tau=1, 
                          volatility=0.05,
                          spot_bid_price_skew=2,
                          spot_ask_price_skew=2,
                          spot_bid_size_skew=2,
                          spot_ask_size_skew=2,
                          future_bid_price_skew=2,
                          future_ask_price_skew=2,
                          future_bid_size_skew=2,
                          future_ask_size_skew=2,
                          spot_bid_levels=5,
                          spot_ask_levels=5,
                          future_bid_levels=5,
                          future_ask_levels=5,
                          spot_q_skew=1,
                          future_q_skew=1,
                          tick_size=0.05,
                          lot_size=0.001,
                          max_quote_size=1)
                          
    strategy = MultiMMStrategy("test_strategy", quoter, 2, 1, spot_instr, future_instr, 360, 200, df.shape[0])
    exch.register(strategy)
    exch.start(Data(df, 100))
    
    iter = 0
    print("total steps=", df.shape[0])
    while exch.step():
        if iter % 500 == 0:
            print("iter=", iter)
        iter += 1
    
    strategy.spot_position.stat.summary("perp")
    strategy.future_position.stat.summary("future")