import numpy as np

from .common import *
from .stock_universe import ThreeSigmaStockUniverse
from typing import List, Optional
import datetime

_WATCHING_WINDOW = 12


class VolumeBreakoutProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_universe = ThreeSigmaStockUniverse(start_time=lookback_start_date,
                                                       end_time=lookback_end_date,
                                                       data_source=data_source)
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
        intraday_closes = intraday_lookback['Close'][p:]
        intraday_volumes = intraday_lookback['Volume'][p:]

        if len(intraday_closes) < _WATCHING_WINDOW:
            return

        vwap = context.vwap
        current_distance = context.current_price - vwap[-1]
        if current_distance > 0:
            side = 'long'
            action_type = ActionType.BUY_TO_OPEN
        else:
            side = 'short'
            action_type = ActionType.SELL_TO_OPEN

        for i in range(2, _WATCHING_WINDOW + 1):
            if (intraday_closes[-i] - vwap[-i]) * current_distance > 0:
                return

        if intraday_volumes[-1] < 3 * np.max(intraday_volumes[-_WATCHING_WINDOW:-1]):
            return

        self._hold_positions[context.symbol] = {'side': side,
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
        prev_close = context.intraday_lookback['Close'][-1]
        prev_open = context.intraday_lookback['Open'][-1]
        current_price = context.current_price
        entry_price = position['entry_price']
        side = position['side']
        stop_loss = context.vwap[-1]
        if side == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            if current_price < stop_loss * 0.99:
                return _pop_position()
            if current_price > entry_price * 1.01 and prev_close < prev_open:
                return _pop_position()
        else:
            action = Action(symbol, ActionType.BUY_TO_CLOSE, 1, current_price)
            if current_price > stop_loss * 1.01:
                return _pop_position()
            if current_price < entry_price * 0.99 and prev_close > prev_open:
                return _pop_position()
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            return _pop_position()


class VolumeBreakoutProcessorFactory(ProcessorFactory):

    def __init__(self, enable_model=True):
        super().__init__()
        self._enable_model = enable_model

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> VolumeBreakoutProcessor:
        return VolumeBreakoutProcessor(lookback_start_date, lookback_end_date, data_source)
