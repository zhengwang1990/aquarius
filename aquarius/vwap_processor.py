from .common import *
from .stock_universe import create_stock_universe
from typing import List, Optional
import datetime
import numpy as np
import ta.momentum as momentum

_WATCHING_WINDOW = 12


class VwapProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_unviverse = create_stock_universe(start_time=lookback_start_date,
                                                      end_time=lookback_end_date,
                                                      data_source=data_source)
        self._stock_unviverse.set_dollar_volume_filter(low=1E7, high=2E7)
        self._stock_unviverse.set_average_true_range_percent_filter(low=0.05)
        self._stock_unviverse.set_price_filer(low=5)
        self._hold_positions = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_unviverse.get_stock_universe(view_time)

    def handle_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(14, 0)
                or context.current_time.time() <= datetime.time(11, 00)):
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
        for distance in vwap_distances:
            if np.sign(distance) != distance_sign:
                return

        if distance_sign > 0:
            direction = 'long'
            action_type = ActionType.BUY_TO_OPEN
        else:
            direction = 'short'
            action_type = ActionType.SELL_TO_OPEN

        nearest_distance = np.min(np.abs(vwap_distances))
        if nearest_distance > intraday_range * 0.05:
            return

        if np.abs(context.current_price - context.vwap[-1]) > 0.01 * context.current_price:
            return

        rsi = momentum.rsi(closes, window=6).values[-1]
        if direction == 'long' and rsi <= 40:
            return
        if direction == 'short' and rsi >= 60:
            down_trend = True

        self._hold_positions[context.symbol] = {'direction': direction,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._hold_positions[context.symbol]
        entry_time = position['entry_time']
        prev_close = context.intraday_lookback['Close'][-1]
        prev_open = context.intraday_lookback['Open'][-1]
        entry_price = position['entry_price']
        if position['direction'] == 'long':
            action = Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
            if prev_close < context.vwap[-1]:
                self._hold_positions.pop(context.symbol)
                return action
            if context.current_price > entry_price * 1.01 and prev_close < prev_open:
                return action
        else:
            action = Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)
            if prev_close > context.vwap[-1]:
                self._hold_positions.pop(context.symbol)
                return action
            if context.current_price < entry_price * 0.99 and prev_close > prev_open:
                return action
        if (context.current_time - entry_time >= datetime.timedelta(minutes=30) or
                context.current_time.time() >= datetime.time(15, 55)):
            self._hold_positions.pop(context.symbol)
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
