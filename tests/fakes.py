import alpharius
import collections
import datetime
import unittest.mock as mock

Clock = collections.namedtuple('Clock', ['next_open', 'next_close'])
Asset = collections.namedtuple('Asset', ['symbol', 'tradable', 'marginable',
                                         'shortable', 'easy_to_borrow'])
Account = collections.namedtuple('Account', ['equity', 'cash'])
Position = collections.namedtuple('Position', ['symbol', 'qty', 'current_price',
                                               'market_value', 'cost_basis',
                                               'avg_entry_price'])
Order = collections.namedtuple('Order', ['id', 'symbol', 'side',
                                         'qty', 'notional', 'filled_qty'])
PolygonResponse = collections.namedtuple('PolygonResponse', ['status', 'results'])


class FakeAlpaca:

    def __init__(self):
        self.get_account_call_count = 0
        self.list_assets_call_count = 0
        self.get_clock_call_count = 0
        self.list_orders_call_count = 0
        self.list_positions_call_count = 0
        self.submit_order_call_count = 0
        self.cancel_order_call_count = 0

    def get_account(self):
        self.get_account_call_count += 1
        return Account('2000', '2000')

    def list_assets(self):
        self.list_assets_call_count += 1
        return [Asset(symbol, True, True, True, True)
                for symbol in ['QQQ', 'SPY', 'DIA']]

    def list_positions(self):
        self.list_positions_call_count += 1
        return [Position('QQQ', '10', '10.0', '100.0', '99.0', '9.9')]

    def get_clock(self):
        self.get_clock_call_count += 1
        next_open = mock.Mock()
        next_open.timestamp.return_value = 1615987800
        next_close = mock.Mock()
        next_close.timestamp.return_value = 1616007600
        return Clock(next_open, next_close)

    def list_orders(self, *args, **kwargs):
        self.list_orders_call_count += 1
        return [Order('ORDER123', 'DIA', 'short', None, '123', None),
                Order('ORDER123', 'SPY', 'long', '12', None, '1')]

    def submit_order(self, *args, **kwargs):
        self.submit_order_call_count += 1

    def cancel_order(self, *args, **kwargs):
        self.cancel_order_call_count += 1


class FakePolygon:

    def __init__(self):
        self.stocks_equities_aggregates_call_count = 0

    def stocks_equities_aggregates(self, *args, **kwargs):
        self.stocks_equities_aggregates_call_count += 1
        results = [{'t': '1616000000000', 'o': 50, 'h': 51, 'l': 49, 'c': 50.5, 'vw': 50.123, 'v': 100},
                   {'t': '1616000300000', 'o': 51, 'h': 52, 'l': 50, 'c': 51.5, 'vw': 51.123, 'v': 110},
                   {'t': '1616000600000', 'o': 52, 'h': 52.5, 'l': 50, 'c': 51.7, 'vw': 52.234, 'v': 120},
                   {'t': '1616000900000', 'o': 51, 'h': 52, 'l': 50, 'c': 51.5, 'vw': 51.123, 'v': 120}]
        return PolygonResponse('OK', results)


class FakeProcess(alpharius.Processor):
    def __init__(self):
        super().__init__()
        self.get_stock_universe_call_count = 0
        self.process_data_call_count = 0

    def get_stock_universe(self, view_time):
        return ['QQQ', 'SPY', 'DIA']

    def process_data(self, context):
        self.process_data_call_count += 1
        if context.current_time == datetime.time(10, 0) and context.symbol == 'QQQ':
            return alpharius.Action('QQQ', alpharius.ActionType.BUY_TO_OPEN, 1, 51)
        if context.current_time == datetime.time(10, 0) and context.symbol == 'DIA':
            return alpharius.Action('DIA', alpharius.ActionType.BUY_TO_OPEN, 1, 51)
        if context.current_time == datetime.time(11, 30) and context.symbol == 'QQQ':
            return alpharius.Action('QQQ', alpharius.ActionType.SELL_TO_CLOSE, 1, 52)
        if context.current_time == datetime.time(12, 0) and context.symbol == 'DIA':
            return alpharius.Action('DIA', alpharius.ActionType.SELL_TO_CLOSE, 1, 52)
        if context.current_time == datetime.time(13, 0) and context.symbol == 'DIA':
            return alpharius.Action('DIA', alpharius.ActionType.SELL_TO_OPEN, 1, 52)
        if context.current_time == datetime.time(13, 10) and context.symbol == 'DIA':
            return alpharius.Action('DIA', alpharius.ActionType.BUY_TO_CLOSE, 1, 50)
        if context.current_time == datetime.time(16, 0) and context.symbol == 'SPY':
            return alpharius.Action('SPY', alpharius.ActionType.BUY_TO_OPEN, 1, 50)


class FakeProcessorFactory(alpharius.ProcessorFactory):

    def __init__(self):
        super().__init__()
        self.create_call_count = 0

    def create(self, *args, **kwargs):
        self.create_call_count += 1
        return FakeProcess()
