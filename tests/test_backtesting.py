from .fakes import *
from parameterized import parameterized
import alpaca_trade_api as tradeapi
import alpharius
import itertools
import matplotlib.pyplot as plt
import os
import pandas_market_calendars as mcal
import pandas as pd
import polygon
import unittest
import unittest.mock as mock


class TestTrading(unittest.TestCase):

    def setUp(self):
        self.patch_open = mock.patch('builtins.open', mock.mock_open())
        self.patch_open.start()
        self.patch_isfile = mock.patch.object(os.path, 'isfile', return_value=False)
        self.patch_isfile.start()
        self.patch_mkdirs = mock.patch.object(os, 'makedirs')
        self.patch_mkdirs.start()
        self.patch_savefig = mock.patch.object(plt, 'savefig')
        self.mock_savefig = self.patch_savefig.start()
        self.patch_tight_layout = mock.patch.object(plt, 'tight_layout')
        self.patch_tight_layout.start()
        self.patch_alpaca = mock.patch.object(tradeapi, 'REST', return_value=FakeAlpaca())
        self.patch_alpaca.start()
        self.fake_polygon = FakePolygon()
        self.patch_polygon = mock.patch.object(polygon, 'RESTClient', return_value=self.fake_polygon)
        self.patch_polygon.start()
        self.patch_get_calendar = mock.patch.object(mcal, 'get_calendar', return_value=mock.Mock())
        self.patch_get_calendar.start()
        self.patch_date_range = mock.patch.object(
            mcal, 'date_range',
            side_effect=itertools.chain(
                [[pd.to_datetime('2021-03-17')]],
                itertools.repeat([pd.to_datetime('2021-02-17') + datetime.timedelta(days=i) for i in range(60)])))
        self.patch_date_range.start()
        os.environ['POLYGON_API_KEY'] = 'fake_polygon_api_key'

    def tearDown(self):
        self.patch_open.stop()
        self.patch_isfile.stop()
        self.patch_mkdirs.stop()
        self.patch_savefig.stop()
        self.patch_tight_layout.stop()
        self.patch_alpaca.stop()
        self.patch_polygon.stop()
        self.patch_get_calendar.stop()
        self.patch_date_range.stop()

    @parameterized.expand([(alpharius.TradingFrequency.FIVE_MIN,),
                           (alpharius.TradingFrequency.CLOSE_TO_CLOSE,),
                           (alpharius.TradingFrequency.CLOSE_TO_OPEN,)])
    def test_run_success(self, trading_frequency):
        fake_processor_factory = FakeProcessorFactory(trading_frequency)
        fake_processor = fake_processor_factory.processor
        backtesting = alpharius.Backtesting(start_date=pd.to_datetime('2021-03-17'),
                                            end_date=pd.to_datetime('2021-03-18'),
                                            processor_factories=[fake_processor_factory])

        backtesting.run()

        self.assertGreater(fake_processor.get_stock_universe_call_count, 0)
        self.assertGreater(fake_processor.process_data_call_count, 0)

    def test_run_with_processors(self):
        processor_factories = [alpharius.LevelBreakoutProcessorFactory(),
                               alpharius.SwingProcessorFactory(),
                               alpharius.MetricRankingProcessorFactory()]
        backtesting = alpharius.Backtesting(start_date=pd.to_datetime('2021-03-17'),
                                            end_date=pd.to_datetime('2021-03-18'),
                                            processor_factories=processor_factories)

        backtesting.run()


if __name__ == '__main__':
    unittest.main()
