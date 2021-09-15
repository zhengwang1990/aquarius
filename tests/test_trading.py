from .fakes import *
import alpaca_trade_api as tradeapi
import alpharius
import itertools
import os
import polygon
import time
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
        self.patch_sleep = mock.patch.object(time, 'sleep')
        self.patch_sleep.start()
        self.patch_time = mock.patch.object(time, 'time', side_effect=itertools.count(1615987700))
        self.patch_time.start()
        self.fake_alpaca = FakeAlpaca()
        self.patch_alpaca = mock.patch.object(tradeapi, 'REST', return_value=self.fake_alpaca)
        self.patch_alpaca.start()
        self.patch_polygon = mock.patch.object(polygon, 'RESTClient', return_value=FakePolygon())
        self.patch_polygon.start()
        self.trading = alpharius.Trading(processor_factories=[FakeProcessorFactory()])

    def tearDown(self):
        self.patch_open.stop()
        self.patch_isfile.stop()
        self.patch_mkdirs.stop()
        self.patch_sleep.stop()
        self.patch_time.stop()
        self.patch_alpaca.stop()
        self.patch_polygon.stop()

    def test_run_success(self):
        self.trading.run()

        self.assertGreater(self.fake_alpaca.list_orders_call_count, 0)
        self.assertGreater(self.fake_alpaca.list_positions_call_count, 0)
        self.assertGreater(self.fake_alpaca.submit_order_call_count, 0)
        self.assertGreater(self.fake_alpaca.get_account_call_count, 0)
        self.assertGreater(self.fake_alpaca.cancel_order_call_count, 0)


if __name__ == '__main__':
    unittest.main()
