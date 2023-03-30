# -*- coding: utf-8 -*-
from mmtester import as_quoter as ASQ
from mmtester import exchange as exchange
from mmtester import single_mm_strategy as mm_strat
from mmtester import inverse_instrument as instrument
import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        exch = exchange.Exchange(500, 500)
        instr = instrument.InverseInstrument("perp")
        quoter = ASQ.ASQuoter(instr, 0, 0, 0, 1, 0.1, 2, 2, 0.05, 0.01, 1)
        strategy = mm_strat.SingleMMStrategy("test_strategy", quoter, 2, instr,  3600, 5, 10)
        exch.register(strategy)
        exch.start()
        self.assertTrue(exch.step())
                                                                          


if __name__ == '__main__':
    unittest.main()