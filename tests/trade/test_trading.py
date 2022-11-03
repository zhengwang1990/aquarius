import os
import email.mime.image as image
import email.mime.multipart as multipart
import itertools
import time
import smtplib

import pytest
from alpharius import trade
from alpharius.trade import processors
from ..fakes import Account, FakeAlpaca, FakeProcessorFactory


@pytest.fixture(autouse=True)
def mock_time(mocker):
    mocker.patch.object(time, 'sleep')
    mocker.patch.object(time, 'time', side_effect=itertools.count(1615987700))


@pytest.fixture(autouse=True)
def mock_email(mocker):
    mocker.patch.object(image, 'MIMEImage', autospec=True)
    mocker.patch.object(multipart.MIMEMultipart, 'as_string', return_value='')
    os.environ['POLYGON_API_KEY'] = 'fake_polygon_api_key'
    os.environ['EMAIL_USERNAME'] = 'fake_user'
    os.environ['EMAIL_PASSWORD'] = 'fake_password'
    os.environ['EMAIL_RECEIVER'] = 'fake_receiver'


@pytest.fixture(autouse=True)
def mock_cash_reserve():
    os.environ['CASH_RESERVE'] = '0'


@pytest.fixture(autouse=True)
def mock_smtp(mocker):
    return mocker.patch.object(smtplib, 'SMTP', autospec=True)


@pytest.mark.parametrize("trading_frequency",
                         [trade.TradingFrequency.FIVE_MIN,
                          trade.TradingFrequency.CLOSE_TO_CLOSE,
                          trade.TradingFrequency.CLOSE_TO_OPEN])
def test_run_success(mock_alpaca, mock_smtp, trading_frequency):
    fake_processor_factory = FakeProcessorFactory(trading_frequency)
    fake_processor = fake_processor_factory.processor
    trading = trade.Trading(processor_factories=[fake_processor_factory])

    trading.run()

    assert mock_alpaca.list_orders_call_count > 0
    assert mock_alpaca.list_positions_call_count > 0
    assert mock_alpaca.submit_order_call_count > 0
    assert mock_alpaca.get_account_call_count > 0
    assert fake_processor.get_stock_universe_call_count > 0
    assert fake_processor.process_data_call_count > 0
    mock_smtp.assert_called_once()


def test_run_with_processors(mock_smtp):
    processor_factories = [processors.OvernightProcessorFactory(),
                           processors.ZScoreProcessorFactory(),
                           processors.O2lProcessorFactory(),
                           processors.O2hProcessorFactory(),
                           processors.BearMomentumProcessorFactory(),
                           processors.HourlyReversionProcessorFactory()]
    trading = trade.Trading(processor_factories=processor_factories)

    trading.run()

    mock_smtp.assert_called_once()


def test_not_run_on_market_close_day(mocker, mock_alpaca):
    trading = trade.Trading(processor_factories=[])
    mocker.patch.object(FakeAlpaca, 'get_calendar', return_value=[])

    trading.run()

    assert mock_alpaca.get_account_call_count > 0
    assert mock_alpaca.get_bars_call_count == 0


def test_small_position_not_open(mocker, mock_alpaca):
    fake_processor_factory = FakeProcessorFactory(
        trade.TradingFrequency.CLOSE_TO_OPEN)
    trading = trade.Trading(processor_factories=[fake_processor_factory])
    mocker.patch.object(FakeAlpaca, 'get_account',
                        return_value=Account('2000', '0.1'))

    trading.run()

    assert mock_alpaca.submit_order_call_count == 0


def test_trade_transactions_executed(mocker, mock_alpaca):
    trading = trade.Trading(processor_factories=[])
    expected_transactions = [
        {'symbol': 'A', 'action_type': trade.ActionType.BUY_TO_OPEN,
         'qty': None, 'side': 'buy', 'notional': 900},
        {'symbol': 'B', 'action_type': trade.ActionType.SELL_TO_OPEN,
         'qty': 9, 'side': 'sell', 'notional': None},
        {'symbol': 'QQQ', 'action_type': trade.ActionType.SELL_TO_CLOSE,
         'qty': 10, 'side': 'sell', 'notional': None},
        {'symbol': 'GOOG', 'action_type': trade.ActionType.BUY_TO_CLOSE,
         'qty': 10, 'side': 'buy', 'notional': None},
    ]
    actions = [trade.Action(t['symbol'], t['action_type'], 1, 100, 'Processor')
               for t in expected_transactions]
    mocker.patch.object(FakeAlpaca, 'submit_order')

    trading._trade(actions)

    for t in expected_transactions:
        mock_alpaca.submit_order.assert_any_call(
            symbol=t['symbol'], qty=t['qty'], side=t['side'],
            type='market', time_in_force='day', notional=t['notional'],
            limit_price=None)


def test_trade_transactions_skipped(mock_alpaca):
    trading = trade.Trading(processor_factories=[])
    actions = [trade.Action('QQQ', trade.ActionType.BUY_TO_CLOSE, 1, 100, 'Processor'),
               trade.Action('GOOG', trade.ActionType.SELL_TO_CLOSE, 1, 100, 'Processor'),
               trade.Action('AAPL', trade.ActionType.SELL_TO_CLOSE, 1, 100, 'Processor')]

    trading._trade(actions)

    assert mock_alpaca.submit_order_call_count == 0
