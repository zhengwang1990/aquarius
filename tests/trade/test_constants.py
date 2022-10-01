import alpharius.trade as trade
import pandas as pd
import unittest


class TestConstants(unittest.TestCase):

    def test_get_nasdaq100(self):
        nasdaq100_symbols = trade.get_nasdaq100(pd.to_datetime('2015-01-01'))
        self.assertIn('AAPL', nasdaq100_symbols)

    def test_get_sp500(self):
        sp500_symbols = trade.get_sp500(pd.to_datetime('2015-01-01'))
        self.assertIn('AAPL', sp500_symbols)


if __name__ == '__main__':
    unittest.main()
