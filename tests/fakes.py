import collections
import contextlib
import datetime
import itertools
import time
import unittest.mock as mock

import pandas as pd
from alpharius import trade
from alpharius.utils import TIME_ZONE

Clock = collections.namedtuple('Clock', ['next_open', 'next_close'])
ClockTimestamp = collections.namedtuple('ClockTimestamp', ['timestamp'])
Asset = collections.namedtuple('Asset', ['symbol', 'tradable', 'marginable',
                                         'shortable', 'easy_to_borrow', 'fractionable'])
Account = collections.namedtuple('Account', ['equity', 'cash'])
Position = collections.namedtuple('Position', ['symbol', 'qty', 'current_price',
                                               'market_value', 'cost_basis',
                                               'avg_entry_price', 'change_today',
                                               'unrealized_plpc'])
Order = collections.namedtuple('Order', ['id', 'symbol', 'side', 'qty', 'notional',
                                         'filled_qty', 'filled_at', 'filled_avg_price',
                                         'submitted_at'])
Bar = collections.namedtuple('Bar', ['t', 'o', 'h', 'l', 'c', 'vw', 'v'])
History = collections.namedtuple('History', ['equity', 'timestamp'])
Calendar = collections.namedtuple('Calendar', ['date', 'open', 'close'])
Trade = collections.namedtuple('Trade', ['p'])
Agg = collections.namedtuple(
    'Agg', ['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume'])
LastTrade = collections.namedtuple('LastTrade', ['price'])


def _to_timestamp(t) -> int:
    time_obj = pd.to_datetime(t)
    if not time_obj.tzinfo:
        time_obj.tz_localize(TIME_ZONE)
    return int(time_obj.timestamp())


class FakeAlpaca:

    def __init__(self):
        self.get_account_call_count = 0
        self.list_assets_call_count = 0
        self.get_clock_call_count = 0
        self.list_orders_call_count = 0
        self.list_positions_call_count = 0
        self.submit_order_call_count = 0
        self.cancel_order_call_count = 0
        self.get_portfolio_history_call_count = 0
        self.get_bars_call_count = 0
        self.get_calendar_call_count = 0
        self.get_latest_trades_call_count = 0
        self._value_cycle = itertools.cycle([42, 40, 41, 43, 42, 41.5, 40,
                                             41, 42, 38, 41, 42])

    def get_account(self):
        self.get_account_call_count += 1
        return Account('2000', '2000')

    def list_assets(self):
        self.list_assets_call_count += 1
        return [Asset(symbol, True, True, True, True, True)
                for symbol in ['QQQ', 'SPY', 'DIA', 'TQQQ', 'GOOG', 'AAPL', 'MSFT'
                               'UCO', 'TSLA']]

    def list_positions(self):
        self.list_positions_call_count += 1
        return [Position('QQQ', '10', '10.0', '100.0', '99.0', '9.9', '0.01', '0'),
                Position('GOOG', '-10', '94.4', '100.0', '99.0', '10', '0.01', '0')]

    def get_clock(self):
        self.get_clock_call_count += 1
        next_open = ClockTimestamp(lambda: 1615987800)
        next_close = ClockTimestamp(lambda: 1616011200)
        return Clock(next_open, next_close)

    def list_orders(self, status=None, direction=None, *args, **kwargs):
        self.list_orders_call_count += 1
        if self.list_orders_call_count % 3 == 0 and status != 'closed':
            return []
        orders = [Order('ORDER122', 'DIA', 'sell', '14', None, '0',
                        pd.to_datetime('2021-03-17T10:14:57.0Z'), '12',
                        pd.to_datetime('2021-03-17T10:14:57.0Z')),
                  Order('ORDER124', 'SPY', 'buy', '12', None, '1',
                        pd.to_datetime('2021-03-17T10:20:00.0Z'), '13',
                        pd.to_datetime('2021-03-17T10:20:00.0Z')),
                  Order('ORDER123', 'DIA', 'buy', '14', None, '0',
                        pd.to_datetime('2021-03-17T10:15:57.0Z'), '9',
                        pd.to_datetime('2021-03-17T10:15:57.0Z')),
                  Order('ORDER125', 'QQQ', 'buy', None, '100.1', '10',
                        pd.to_datetime(time.time() - 3, utc=True, unit='s'), '9.1',
                        pd.to_datetime(time.time() - 4, utc=True, unit='s')),
                  Order('ORDER126', 'QQQ', 'sell', None, '100.1', '10',
                        pd.to_datetime(time.time() - 1, utc=True, unit='s'), '9.2',
                        pd.to_datetime(time.time() - 2, utc=True, unit='s')),
                  Order('ORDER127', 'QQQ', 'buy', None, '100.1', '10',
                        pd.to_datetime(time.time(), utc=True, unit='s'), '9.1',
                        pd.to_datetime(time.time(), utc=True, unit='s'))]
        if direction == 'desc':
            orders = orders[::-1]
        return orders

    def submit_order(self, *args, **kwargs):
        self.submit_order_call_count += 1

    def cancel_order(self, *args, **kwargs):
        self.cancel_order_call_count += 1

    def get_portfolio_history(self, date_start, date_end, timeframe, *args, **kwargs):
        self.get_portfolio_history_call_count += 1
        if timeframe == '1D':
            time_interval = 86400
        elif timeframe == '1H':
            time_interval = 3600
        elif timeframe == '5Min':
            time_interval = 300
        else:
            raise ValueError('Time frame must be 5Min, 1H or 1D.')
        start_time = _to_timestamp(date_start)
        start_time -= start_time % time_interval
        end_time = _to_timestamp(date_end) + time_interval
        timestamps = [t for t in range(start_time, end_time, time_interval)
                      if pd.to_datetime(t, unit='s', utc=True).isoweekday() < 6]
        if len(timestamps) > 10:
            equity = [0] * 10 + [i * (-1) ** i + len(timestamps) + 1 for i in range(len(timestamps) - 10)]
        else:
            equity = [i * (-1) ** i + len(timestamps) + 1 for i in range(len(timestamps))]
        return History(equity, timestamps)

    def get_bars(self, symbol, timeframe, start, end, *args, **kwargs):
        self.get_bars_call_count += 1
        if timeframe.value == '1Day':
            time_interval = 86400
        elif timeframe.value == '1Hour':
            time_interval = 3600
        elif timeframe.value == '5Min':
            time_interval = 300
        else:
            raise ValueError('Time frame must be 5 min, 1 hour or 1 day.')
        start_timestamp = _to_timestamp(start)
        start_timestamp -= start_timestamp % time_interval
        end_timestamp = _to_timestamp(end) + time_interval
        return [Bar(pd.to_datetime(t, unit='s', utc=True),
                    40, 41, 39, next(self._value_cycle), 40.123, 10)
                for t in range(start_timestamp, end_timestamp, time_interval)
                if pd.to_datetime(t, unit='s', utc=True).isoweekday() < 6]

    def get_calendar(self, start, end, *args, **kwargs):
        self.get_calendar_call_count += 1
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        calendar = []
        date = start_date
        while date <= end_date:
            if date.isoweekday() < 6:
                calendar.append(
                    Calendar(date, datetime.time(9, 30), datetime.time(16, 0)))
            date += datetime.timedelta(days=1)
        return calendar

    def get_latest_trades(self, symbols, *args, **kwargs):
        self.get_latest_trades_call_count += 1
        value = next(self._value_cycle) + 5 * (-1) ** self.get_latest_trades_call_count
        return {symbol: Trade(value) for symbol in symbols}


class FakePolygon:

    def __init__(self):
        self.get_aggs_call_count = 0
        self.get_last_trade_call_count = 0
        self._value_cycle = itertools.cycle([42, 40, 41, 43, 42, 41.5, 40,
                                             41, 42, 35, 41, 42])

    def get_aggs(self, ticker, multiplier, timespan, from_, to, *args, **kwargs):
        self.get_aggs_call_count += 1
        start = pd.to_datetime(from_, unit='ms', utc=True)
        end = pd.to_datetime(to, unit='ms', utc=True)
        if multiplier == 1 and timespan == 'day':
            time_interval = 86400
        elif multiplier == 1 and timespan == 'hour':
            time_interval = 3600
        elif multiplier == 5 and timespan == 'minute':
            time_interval = 300
        else:
            raise ValueError('Time frame must be 5 min, 1 hour or 1 day.')
        start_timestamp = int(start.timestamp())
        start_timestamp -= start_timestamp % time_interval
        return [Agg(t * 1000, 40, 41, 39, next(self._value_cycle), 40.123, 10)
                for t in range(start_timestamp,
                               int(end.timestamp()) + time_interval,
                               time_interval)
                if pd.to_datetime(t, unit='s', utc=True).isoweekday() < 6]

    def get_last_trade(self, symbol, *args, **kwargs):
        self.get_last_trade_call_count += 1
        value = next(self._value_cycle) + 5 * (-1) ** self.get_last_trade_call_count
        return LastTrade(value)


class FakeProcessor(trade.Processor):
    def __init__(self, trading_frequency):
        super().__init__()
        self.get_stock_universe_call_count = 0
        self.process_data_call_count = 0
        self.trading_frequency = trading_frequency

    def get_trading_frequency(self):
        return self.trading_frequency

    def get_stock_universe(self, view_time):
        self.get_stock_universe_call_count += 1
        return ['QQQ', 'SPY', 'DIA']

    def process_data(self, context):
        self.process_data_call_count += 1
        if context.current_time.time() == datetime.time(9, 35) and context.symbol == 'QQQ':
            return trade.ProcessorAction('QQQ', trade.ActionType.BUY_TO_OPEN, 1)
        if context.current_time.time() == datetime.time(10, 0) and context.symbol == 'DIA':
            return trade.ProcessorAction('DIA', trade.ActionType.BUY_TO_OPEN, 1)
        if context.current_time.time() == datetime.time(11, 30) and context.symbol == 'QQQ':
            return trade.ProcessorAction('QQQ', trade.ActionType.SELL_TO_CLOSE, 0.5)
        if context.current_time.time() == datetime.time(12, 0) and context.symbol == 'DIA':
            return trade.ProcessorAction('DIA', trade.ActionType.SELL_TO_CLOSE, 1)
        if context.current_time.time() == datetime.time(13, 0) and context.symbol == 'DIA':
            return trade.ProcessorAction('DIA', trade.ActionType.SELL_TO_OPEN, 1)
        if context.current_time.time() == datetime.time(13, 10) and context.symbol == 'DIA':
            return trade.ProcessorAction('DIA', trade.ActionType.BUY_TO_CLOSE, 1)
        if context.current_time.time() == datetime.time(16, 0) and context.symbol == 'SPY':
            return trade.ProcessorAction('SPY', trade.ActionType.BUY_TO_OPEN, 1)


class FakeProcessorFactory(trade.ProcessorFactory):

    def __init__(self, trading_frequency: trade.TradingFrequency):
        super().__init__()
        self.create_call_count = 0
        self.processor = FakeProcessor(trading_frequency)

    def create(self, *args, **kwargs) -> FakeProcessor:
        self.create_call_count += 1
        return self.processor


class FakeDbEngine:
    def __init__(self):
        self.conn = mock.MagicMock()
        self.disconnect_cnt = 0

    @contextlib.contextmanager
    def connect(self):
        try:
            yield self.conn
        finally:
            self.disconnect_cnt += 1
