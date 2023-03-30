# -*- coding: utf-8 -*-
from mmtester import ASQuoter
from mmtester import Exchange
from mmtester import SingleMMStrategy
from mmtester import InverseInstrument
import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        exch = Exchange(500, 500)
        instr = InverseInstrument("perp")
        quoter = ASQuoter(instr, 0, 0, 0, 1, 0.1, 2, 2, 0.05, 0.01, 1)
        strategy = SingleMMStrategy("test_strategy", quoter, 2, instr,  3600, 5, 10)
        exch.register(strategy)
        exch.start()
        self.assertTrue(exch.step())
                                                                          

if __name__ == '__main__':
    unittest.main()