import pandas as pd
from mmtester.as_quoter import ASQuoter
from mmtester.exchange import Exchange
from mmtester.single_mm_strategy import SingleMMStrategy
from mmtester.inverse_instrument import InverseInstrument
from mmtester.data import Data

if __name__ == '__main__':
    df = pd.read_csv("./mmtester/data_generator/data/data.csv.gz", header=0, index_col=0, parse_dates=[0])
    exch = Exchange(500, 500)
    instr = InverseInstrument("perp", 0, 0.0005)
    quoter = ASQuoter(instr, 0, 0.1, 2, 1, 0.05, 1.5, 1.5, 0.01, 0.01, 2)
    strategy = SingleMMStrategy("test_strategy", quoter, 2, instr,  1800, 3, 240, df.shape[0])
    exch.register(strategy)
    exch.start(Data(df, 500))
    
    iter = 0
    print("total steps=", df.shape[0])
    while exch.step():
        if iter % 500 == 0:
            print("iter=", iter)
        iter += 1
    
    strategy.position.stat.summary()