from mmtester.as_quoter import ASQuoter
from mmtester.exchange import Exchange
from mmtester.single_mm_strategy import SingleMMStrategy
from mmtester.inverse_instrument import InverseInstrument


if __name__ == '__main__':
    exch = Exchange(500, 500)
    instr = InverseInstrument("perp", 0, 0.0005)
    quoter = ASQuoter(instr, 0, 0, 0, 1, 0.1, 2, 2, 0.05, 0.01, 1)
    strategy = SingleMMStrategy("test_strategy", quoter, 2, instr,  3600, 5, 10)
    exch.register(strategy)
    exch.start()
    assert(exch.step())
