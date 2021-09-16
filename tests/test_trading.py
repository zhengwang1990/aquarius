from .fakes import *
import alpaca_trade_api as tradeapi
import alpharius
import email.mime.image as image
import email.mime.multipart as multipart
import itertools
import matplotlib.pyplot as plt
import os
import pandas_market_calendars as mcal
import polygon
import smtplib
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
        self.patch_get_calendar = mock.patch.object(mcal, 'get_calendar', return_value=mock.Mock())
        self.patch_get_calendar.start()
        self.patch_date_range = mock.patch.object(
            mcal, 'date_range',
            return_value=[pd.to_datetime('2021-03-08') + datetime.timedelta(days=i) for i in range(10)])
        self.patch_date_range.start()
        self.patch_smtp = mock.patch.object(smtplib, 'SMTP', autospec=True)
        self.patch_smtp.start()
        self.patch_savefig = mock.patch.object(plt, 'savefig')
        self.patch_savefig.start()
        self.patch_image = mock.patch.object(image, 'MIMEImage', autospec=True)
        self.patch_image.start()
        self.patch_multipart = mock.patch.object(multipart.MIMEMultipart, 'as_string', return_value='')
        self.patch_multipart.start()
        os.environ['POLYGON_API_KEY'] = 'fake_polygon_api_key'
        os.environ['EMAIL_USERNAME'] = 'fake_user'
        os.environ['EMAIL_PASSWORD'] = 'fake_password'
        os.environ['EMAIL_RECEIVER'] = 'fake_receiver'
        os.environ['CASH_RESERVE'] = '0'

    def tearDown(self):
        self.patch_open.stop()
        self.patch_isfile.stop()
        self.patch_mkdirs.stop()
        self.patch_sleep.stop()
        self.patch_time.stop()
        self.patch_alpaca.stop()
        self.patch_polygon.stop()
        self.patch_get_calendar.stop()
        self.patch_date_range.stop()
        self.patch_smtp.stop()
        self.patch_image.stop()
        self.patch_multipart.stop()

    def test_run_success(self):
        fake_processor_factory = FakeProcessorFactory()
        fake_processor = fake_processor_factory.processor
        trading = alpharius.Trading(processor_factories=[fake_processor_factory])

        trading.run()

        self.assertGreater(self.fake_alpaca.list_orders_call_count, 0)
        self.assertGreater(self.fake_alpaca.list_positions_call_count, 0)
        self.assertGreater(self.fake_alpaca.submit_order_call_count, 0)
        self.assertGreater(self.fake_alpaca.get_account_call_count, 0)
        self.assertGreater(self.fake_alpaca.cancel_order_call_count, 0)
        self.assertGreater(fake_processor.get_stock_universe_call_count, 0)
        self.assertGreater(fake_processor.process_data_call_count, 0)

    def test_run_with_processors(self):
        processor_factories = [alpharius.NoopProcessorFactory(),
                               alpharius.VolumeBreakoutProcessorFactory(),
                               alpharius.LevelBreakoutProcessorFactory(),
                               alpharius.SwingProcessorFactory()]
        trading = alpharius.Trading(processor_factories=processor_factories)

        trading.run()


if __name__ == '__main__':
    unittest.main()
