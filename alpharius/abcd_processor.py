from .common import *
from .stock_universe import ThreeSigmaStockUniverse
from typing import List, Optional
import datetime
import numpy as np

_WATCHING_WINDOW = 20
_INTRA_DAY_RANGE_PORTION = 0.05


class AbcdProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 logging_enabled: bool) -> None:
        super().__init__()
        self._stock_universe = ThreeSigmaStockUniverse(start_time=lookback_start_date,
                                                       end_time=lookback_end_date,
                                                       data_source=data_source)
        self._logging_enabled = logging_enabled
        self._hold_positions = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_universe.get_stock_universe(view_time)

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(15, 0)
                or context.current_time.time() <= datetime.time(10, 0)):
            return
        intraday_lookback = context.intraday_lookback
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        if p is None:
            return

        if len(intraday_lookback) < _WATCHING_WINDOW + p:
            return

        intraday_closes = np.array(intraday_lookback['Close'])
        intraday_opens = np.array(intraday_lookback['Open'])
        intraday_highs = np.array(intraday_lookback['High'])
        intraday_lows = np.array(intraday_lookback['Low'])
        intraday_range = np.max(intraday_highs) - np.min(intraday_lows)
        intraday_volumes = np.array(intraday_lookback['Volume'])

        if intraday_closes[-1] < intraday_opens[-1]:
            return

        vwap = context.vwap

        current_index = len(intraday_lookback) - 1
        flat_value = intraday_closes[current_index]
        flat_start = current_index - 1
        for i in range(flat_start - 1, -1, -1):
            if intraday_closes[i] < flat_value:
                flat_value = intraday_closes[i]
            if intraday_closes[i] > flat_value + _INTRA_DAY_RANGE_PORTION * 2 * intraday_range:
                flat_start = i + 1
                break

        if current_index - flat_start < 2 or current_index - flat_start > 10:
            return

        if context.current_price < vwap[-1]:
            return

        if context.current_price - flat_value < _INTRA_DAY_RANGE_PORTION * 2 * intraday_range:
            return

        peak_start = flat_start - 1
        peak_value = intraday_closes[flat_start]
        for i in range(peak_start, -1, -1):
            if intraday_closes[i] > peak_value:
                peak_value = intraday_closes[i]
            if intraday_closes[i] < peak_value - _INTRA_DAY_RANGE_PORTION * 2 * intraday_range:
                peak_start = i + 1
                break

        if peak_start == 0 or peak_start > flat_start - 2 or peak_start < flat_start - 12:
            return

        if peak_value - flat_value < _INTRA_DAY_RANGE_PORTION * 2 * intraday_range:
            return

        if intraday_volumes[-1] < np.max(intraday_volumes[peak_start:-1]):
            return

        trough_value = intraday_closes[peak_start]
        trough_start = peak_start - 1
        for i in range(peak_start - 1, -1, -1):
            if intraday_closes[i] < trough_value:
                trough_value = intraday_closes[i]
            if intraday_closes[i] > trough_value + _INTRA_DAY_RANGE_PORTION * 2 * intraday_range:
                trough_start = i + 1
                break

        if trough_start > peak_start - 2:
            return

        if peak_value - trough_value < _INTRA_DAY_RANGE_PORTION * 6 * intraday_range:
            return

        if trough_value > context.current_price:
            return

        if not (context.current_price - flat_value < peak_value - flat_value):
            return

        if peak_value < context.current_price * 1.01:
            return

        side = 'long'
        action_type = ActionType.BUY_TO_OPEN

        take_profit = peak_value

        self._hold_positions[context.symbol] = {'side': side,
                                                'take_profit': take_profit,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        def _pop_position():
            self._hold_positions.pop(symbol)
            return action

        symbol = context.symbol
        position = self._hold_positions[symbol]
        entry_time = position['entry_time']
        entry_price = position['entry_price']
        current_price = context.current_price
        prev_close = context.intraday_lookback['Close'][-1]
        prev_open = context.intraday_lookback['Open'][-1]
        side = position['side']
        take_profit = position['take_profit']
        vwap = context.vwap
        intraday_highs = np.array(context.intraday_lookback['High'])
        intraday_lows = np.array(context.intraday_lookback['Low'])
        intraday_range = np.max(intraday_highs) - np.min(intraday_lows)

        if side == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            if current_price < vwap[-1] - 0.05 * intraday_range:
                return _pop_position()
            if current_price > take_profit or (current_price > entry_price * 1.01 and prev_close < prev_open):
                return _pop_position()
        else:
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            return
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            return _pop_position()


class AbcdProcessorFactory(ProcessorFactory):

    def __init__(self, enable_model=True):
        super().__init__()
        self._enable_model = enable_model

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> AbcdProcessor:
        return AbcdProcessor(lookback_start_date, lookback_end_date, data_source, logging_enabled)
