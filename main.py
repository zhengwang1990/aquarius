from aquarius import *
import pandas as pd
import collections
import unittest.mock as mock
import alpaca_trade_api as tradeapi

Asset = collections.namedtuple('Asset', ['symbol', 'tradable', 'marginable',
                                         'shortable', 'easy_to_borrow'])
assets = [Asset(symbol, True, True, True, True) for symbol in ['GOOG', 'AAPL', 'AMZN', 'FB', 'MSFT']]
patch = mock.patch.object(tradeapi.REST, 'list_assets', return_value=assets)
patch.start()

universe = StockUniverse()

universe.set_data_window(pd.to_datetime('2020-07-24'), pd.to_datetime('2021-07-24'), DataSource.YAHOO)

universe.set_average_true_range_percent_filter(low=0.02)

print(universe.get_stock_universe(pd.to_datetime('2020-12-05')))