from .common import *
from .stock_universe import StockUniverse
from typing import List, Optional
import datetime
import numpy as np

_WATCHING_WINDOW = 12


class VwapProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_unviverse = VwapStockUniverse(start_time=lookback_start_date,
                                                  end_time=lookback_end_date,
                                                  data_source=data_source)
        self._stock_unviverse.set_dollar_volume_filter(low=1E7)
        self._stock_unviverse.set_average_true_range_percent_filter(low=0.01)
        self._stock_unviverse.set_price_filer(low=1)
        self._hold_positions = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_unviverse.get_stock_universe(view_time)

    def handle_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(15, 0)
                or context.current_time.time() <= datetime.time(10, 00)):
            return
        intraday_lookback = context.intraday_lookback
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        if p is None:
            return
        intraday_lookback = intraday_lookback.iloc[p:]
        if len(intraday_lookback) < _WATCHING_WINDOW:
            return

        closes = intraday_lookback['Close']
        highs = intraday_lookback['High']
        lows = intraday_lookback['Low']

        intraday_low = np.min(lows)
        intraday_high = np.max(highs)
        intraday_range = intraday_high - intraday_low

        vwap_distances = []
        for i in range(1, _WATCHING_WINDOW + 1):
            vwap_distances.append(closes[-i] - context.vwap[-i])

        distance_sign = np.sign(vwap_distances[0])
        if np.sign(vwap_distances[1]) != distance_sign:
            return
        for distance in vwap_distances[2:]:
            if np.sign(distance) == distance_sign:
                return

        if distance_sign > 0:
            direction = 'long'
            action_type = ActionType.BUY_TO_OPEN
        else:
            direction = 'short'
            action_type = ActionType.SELL_TO_OPEN

        nearest_distance = np.min(np.abs(vwap_distances))
        if nearest_distance > intraday_range * 0.1:
            return

        if np.abs(context.current_price - context.vwap[-1]) > 0.01 * context.current_price:
            return

        if direction == 'long':
            if context.prev_day_close < context.interday_lookback['Close'][-2]:
                return
        if direction == 'short':
            if context.prev_day_close > context.interday_lookback['Close'][-2]:
                return

        self._hold_positions[context.symbol] = {'direction': direction,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        symbol = context.symbol
        position = self._hold_positions[symbol]
        entry_time = position['entry_time']
        prev_close = context.intraday_lookback['Close'][-1]
        prev_open = context.intraday_lookback['Open'][-1]
        current_price = context.current_price
        entry_price = position['entry_price']
        if position['direction'] == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            if current_price < context.vwap[-1]:
                self._hold_positions.pop(symbol)
                return action
            if current_price > entry_price * 1.01 and prev_close < prev_open:
                self._hold_positions.pop(symbol)
                return action
        else:
            action = Action(symbol, ActionType.BUY_TO_CLOSE, 1, current_price)
            if current_price > context.vwap[-1]:
                self._hold_positions.pop(symbol)
                return action
            if current_price < entry_price * 0.99 and prev_close > prev_open:
                self._hold_positions.pop(symbol)
                return action
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            self._hold_positions.pop(symbol)
            return action


class VwapProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> VwapProcessor:
        return VwapProcessor(lookback_start_date, lookback_end_date, data_source)


class VwapStockUniverse(StockUniverse):

    def __init__(self,
                 start_time: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__(start_time, end_time, data_source)

    def get_significant_change(self, symbol: str, prev_day: DATETIME_TYPE) -> bool:
        hist = self._historical_data[symbol]
        p = timestamp_to_index(hist.index, prev_day)
        closes = np.array(hist['Close'][max(p - DAYS_IN_A_MONTH + 1, 1):p + 1])
        changes = np.array([np.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)
                            if closes[i + 1] > 0 and closes[i] > 0])
        if not len(changes):
            return False
        std = np.std(changes)
        mean = np.mean(changes)
        if std < 1E-7:
            return False
        if np.abs((changes[-1] - mean) / std) < 1.5:
            return False
        if np.any(np.abs((changes[-5:-1] - mean) / std) > 1):
            return False
        return True

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        symbols = super().get_stock_universe(view_time)
        res = []
        for symbol in symbols:
            if self.get_significant_change(symbol, prev_day):
                res.append(symbol)
        return res
