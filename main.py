from aquarius import *
import collections
import unittest.mock as mock
import alpaca_trade_api as tradeapi

Asset = collections.namedtuple('Asset', ['symbol', 'tradable', 'marginable',
                                         'shortable', 'easy_to_borrow'])
assets = [Asset(symbol, True, True, True, True) for symbol in ['GOOG', 'AAPL', 'AMZN', 'FB', 'MSFT',
                                                               'QQQ', 'TQQQ', 'SPY']]
patch = mock.patch.object(tradeapi.REST, 'list_assets', return_value=assets)
patch.start()

backtesting = Backtesting(start_date='2020-12-29', end_date='2021-01-06', processor_factories=[NoopProcessorFactory()])

backtesting.run()
