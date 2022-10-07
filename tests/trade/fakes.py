import collections
import datetime
import itertools

import pandas as pd
from alpharius import trade


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
                                         'filled_qty', 'filled_at', 'filled_avg_price'])
Bar = collections.namedtuple('Bar', ['t', 'o', 'h', 'l', 'c', 'vw', 'v'])
History = collections.namedtuple('History', ['equity'])
Calendar = collections.namedtuple('Calendar', ['date', 'open', 'close'])
Trade = collections.namedtuple('Trade', ['p'])
Agg = collections.namedtuple('Agg', ['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume'])
LastTrade = collections.namedtuple('LastTrade', ['price'])


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
        self._value_cycle = itertools.cycle([40, 41, 43, 42, 41.5, 50])

    def get_account(self):
        self.get_account_call_count += 1
        return Account('2000', '2000')

    def list_assets(self):
        self.list_assets_call_count += 1
        return [Asset(symbol, True, True, True, True, True)
                for symbol in ['QQQ', 'SPY', 'DIA', 'TQQQ', 'GOOG', 'AAPL', 'MSFT']]

    def list_positions(self):
        self.list_positions_call_count += 1
        return [Position('QQQ', '10', '10.0', '100.0', '99.0', '9.9', '0.01', '0')]

    def get_clock(self):
        self.get_clock_call_count += 1
        next_open = ClockTimestamp(lambda :1615987800)
        next_close = ClockTimestamp(lambda :1616011200)
        return Clock(next_open, next_close)

    def list_orders(self, *args, **kwargs):
        self.list_orders_call_count += 1
        if self.list_orders_call_count % 3 == 0:
            return []
        return [Order('ORDER123', 'DIA', 'short', '14', None, '0', pd.to_datetime('2021-03-17T10:15:00.0Z'), '12'),
                Order('ORDER123', 'SPY', 'long', '12', None, '1', pd.to_datetime('2021-03-17T10:20:00.0Z'), '13')]

    def submit_order(self, *args, **kwargs):
        self.submit_order_call_count += 1

    def cancel_order(self, *args, **kwargs):
        self.cancel_order_call_count += 1

    def get_portfolio_history(self, *args, **kwargs):
        self.get_portfolio_history_call_count += 1
        return History([i + 100 for i in range(10)])

    def get_bars(self, symbol, timeframe, start, end, *args, **kwargs):
        self.get_bars_call_count += 1
        if timeframe.value == '1Day':
            results = [Bar(pd.to_datetime(t, unit='s', utc=True),
                           40, 41, 39, next(self._value_cycle), 40.123, 10)
                       for t in range(int(pd.to_datetime(start).timestamp()),
                                      int(pd.to_datetime(end).timestamp() + 86400),
                                      86400)
                       if pd.to_datetime(t, unit='s').isoweekday() < 6]
        elif timeframe.value == '5Min':
            day_str = pd.to_datetime(start).strftime('%F')
            results = [Bar(pd.to_datetime(t, unit='s', utc=True),
                           40, 41, 39, next(self._value_cycle), 40.123, 10)
                       for t in range(int(pd.to_datetime(f'{day_str} 09:30:00-04:00').timestamp()),
                                      int(pd.to_datetime(f'{day_str} 16:05:00-04:00').timestamp()),
                                      300)]
        else:
            raise ValueError('Time frame must be 5 min or 1 day.')
        return results

    def get_calendar(self, start, end, *args, **kwargs):
        self.get_calendar_call_count += 1
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        calendar = []
        date = start_date
        while date <= end_date:
            if date.isoweekday() < 6:
                calendar.append(Calendar(date, datetime.time(9, 30), datetime.time(16, 0)))
            date += datetime.timedelta(days=1)
        return calendar

    def get_latest_trades(self, symbols, *args, **kwargs):
        self.get_latest_trades_call_count += 1
        return {symbol: Trade(123) for symbol in symbols}


class FakePolygon:

    def __init__(self):
        self.get_aggs_call_count = 0
        self.get_last_trade_call_count = 0
        self._value_cycle = itertools.cycle([40, 41, 43, 42, 41.5, 50])

    def get_aggs(self, ticker, multiplier, timespan, from_, to, *args, **kwargs):
        self.get_aggs_call_count += 1
        if multiplier == 1 and timespan == 'day':
            start = pd.to_datetime(from_, unit='ms', utc=True)
            end = pd.to_datetime(to, unit='ms', utc=True)
            results = [Agg(t * 1000, 40, 41, 39, next(self._value_cycle), 40.123, 10)
                       for t in range(int(pd.to_datetime(start.date()).timestamp()),
                                      int(pd.to_datetime(end.date()).timestamp() + 86400),
                                      86400)
                       if pd.to_datetime(t, unit='s').isoweekday() < 6]
        elif multiplier == 5 and timespan == 'minute':
            results = [Agg(t * 1000, 40, 41, 39, next(self._value_cycle), 40.123, 10)
                       for t in range(from_ // 1000, to // 1000 + 300, 300)]
        else:
            raise ValueError('Time frame must be 5 min or 1 day.')

        return results

    def get_last_trade(self, symbol, *args, **kwargs):
        self.get_last_trade_call_count += 1
        return LastTrade(123)


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
            return trade.Action('QQQ', trade.ActionType.BUY_TO_OPEN, 1, 51)
        if context.current_time.time() == datetime.time(10, 0) and context.symbol == 'DIA':
            return trade.Action('DIA', trade.ActionType.BUY_TO_OPEN, 1, 51)
        if context.current_time.time() == datetime.time(11, 30) and context.symbol == 'QQQ':
            return trade.Action('QQQ', trade.ActionType.SELL_TO_CLOSE, 1, 52)
        if context.current_time.time() == datetime.time(12, 0) and context.symbol == 'DIA':
            return trade.Action('DIA', trade.ActionType.SELL_TO_CLOSE, 1, 52)
        if context.current_time.time() == datetime.time(13, 0) and context.symbol == 'DIA':
            return trade.Action('DIA', trade.ActionType.SELL_TO_OPEN, 1, 52)
        if context.current_time.time() == datetime.time(13, 10) and context.symbol == 'DIA':
            return trade.Action('DIA', trade.ActionType.BUY_TO_CLOSE, 1, 50)
        if context.current_time.time() == datetime.time(16, 0) and context.symbol == 'SPY':
            return trade.Action('SPY', trade.ActionType.BUY_TO_OPEN, 1, 50)


class FakeProcessorFactory(trade.ProcessorFactory):

    def __init__(self, trading_frequency: trade.TradingFrequency):
        super().__init__()
        self.create_call_count = 0
        self.processor = FakeProcessor(trading_frequency)

    def create(self, *args, **kwargs) -> FakeProcessor:
        self.create_call_count += 1
        return self.processor
