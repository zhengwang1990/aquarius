from .common import *
from .stock_universe import StockUniverse
from typing import List, Optional
import datetime
import numpy as np

_WATCHING_WINDOW = 10


class KeyLevelProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_universe = KeyLevelStockUniverse(start_time=lookback_start_date,
                                                     end_time=lookback_end_date,
                                                     data_source=data_source)
        self._stock_universe.set_dollar_volume_filter(low=1E7, high=1E9)
        self._stock_universe.set_average_true_range_percent_filter(low=0.05, high=0.1)
        self._hold_positions = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_universe.get_stock_universe(view_time)

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(15, 30)
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
        if len(intraday_closes) < _WATCHING_WINDOW:
            return

        intraday_low = np.min(intraday_lookback['Low'])
        intraday_high = np.max(intraday_lookback['High'])
        prev_day_clsoe = context.prev_day_close
        intraday_range = max(intraday_high - intraday_low,
                             intraday_high - prev_day_clsoe,
                             prev_day_clsoe - intraday_low)

        levels = [context.prev_day_close]

        # for i in range(6, len(intraday_closes) - 7):
        #     close = intraday_closes[i]
        #     if close < np.min(intraday_closes[i - 6:i]) and close < np.min(intraday_closes[i + 1:i + 7]):
        #         levels.append(close)
        #     if close > np.max(intraday_closes[i - 6:i]) and close > np.max(intraday_closes[i + 1:i + 7]):
        #         levels.append(close)
        # levels.sort()

        average = np.average(intraday_closes[-_WATCHING_WINDOW:-1])
        distances = [abs(level - average) for level in levels]
        min_i = np.argmin(distances)
        level = levels[min_i]
        threshold = 0.05 * intraday_range

        if abs(context.current_price - level) < threshold:
            return

        for price in intraday_closes[-_WATCHING_WINDOW:-1]:
            if abs(price - level) > threshold:
                return

        if context.current_price > level:
            action_type = ActionType.BUY_TO_OPEN
            side = 'long'
        else:
            action_type = ActionType.SELL_TO_OPEN
            side = 'short'

        current_vwap = context.vwap[-1]
        if side == 'long' and context.current_price < current_vwap:
            return
        if side == 'short' and context.current_price > current_vwap:
            return

        self._hold_positions[context.symbol] = {'level': level,
                                                'side': side,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        def _pop_position():
            self._hold_positions.pop(symbol)
            return action

        symbol = context.symbol
        current_price = context.current_price
        position = self._hold_positions[symbol]
        entry_time = position['entry_time']
        entry_price = position['entry_price']
        level = position['level']
        if position['side'] == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            if current_price < level:
                return _pop_position()
            if current_price - entry_price > 2 * (entry_price - level):
                return _pop_position()
        else:
            action = Action(symbol, ActionType.BUY_TO_CLOSE, 1, current_price)
            if current_price > level:
                return _pop_position()
            if entry_price - current_price > 2 * (level - entry_price):
                return _pop_position()
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            return _pop_position()


class KeyLevelProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> KeyLevelProcessor:
        return KeyLevelProcessor(lookback_start_date, lookback_end_date, data_source)


class KeyLevelStockUniverse(StockUniverse):

    def __init__(self,
                 start_time: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__(start_time, end_time, data_source)

    def get_heavy_volume(self, symbol: str, prev_day: DATETIME_TYPE) -> bool:
        hist = self._historical_data[symbol]
        p = timestamp_to_index(hist.index, prev_day)
        volumes = np.array(hist['Volume'][max(p - DAYS_IN_A_WEEK + 1, 1):p + 1])
        if not len(volumes):
            return False
        if volumes[-1] < 2 * np.average(volumes):
            return False
        return True

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        symbols = super().get_stock_universe(view_time)
        res = []
        for symbol in symbols:
            if self.get_heavy_volume(symbol, prev_day):
                res.append(symbol)
        return res
