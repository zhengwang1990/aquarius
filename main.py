from aquarius import *
import collections
import unittest.mock as mock
import alpaca_trade_api as tradeapi

Asset = collections.namedtuple('Asset', ['symbol', 'tradable', 'marginable',
                                         'shortable', 'easy_to_borrow'])
assets = [Asset(symbol, True, True, True, True) for symbol in ['GOOG', 'AAPL', 'AMZN', 'FB', 'MSFT']]
patch = mock.patch.object(tradeapi.REST, 'list_assets', return_value=assets)
patch.start()

logging_config()

backtesting = Backtesting(start_date='2021-07-20', end_date='2021-07-24', processor_factories=[NoopProcessorFactory()])

backtesting.run()

