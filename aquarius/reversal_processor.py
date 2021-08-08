from .common import *
from .stock_universe import create_stock_universe
from typing import List, Optional
import datetime
import numpy as np
import ta.momentum as momentum


class ReversalProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_unviverse = create_stock_universe(start_time=lookback_start_date,
                                                      end_time=lookback_end_date,
                                                      data_source=data_source)
        self._stock_unviverse.set_dollar_volume_filter(low=1E7, high=1E9)
        self._stock_unviverse.set_average_true_range_percent_filter(low=0.03, high=0.1)
        self._stock_unviverse.set_price_filer(low=5)
        self._hold_positions = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_unviverse.get_stock_universe(view_time)

    def handle_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._handle_position(context)
        if context.current_time.time() >= datetime.time(15, 0):
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
        if len(intraday_lookback) < 13:  # RSI size
            return
        levels = [context.prev_day_close]
        closes = intraday_lookback['Close']
        highs = intraday_lookback['High']
        lows = intraday_lookback['Low']

        up_trend, down_trend = False, False
        rsi = momentum.rsi(closes, window=10).values[-3]
        if rsi > 75:
            up_trend = True
        if rsi < 25:
            down_trend = True
        if not up_trend and not down_trend:
            return

        if down_trend and (closes[-2] < context.vwap[-2] or closes[-1] < context.vwap[-1]
                           or closes[-3] > context.vwap[-3] or closes[-4] > context.vwap[-4]):
            return
        if up_trend and (closes[-2] > context.vwap[-2] or closes[-1] > context.vwap[-1]
                         or closes[-3] < context.vwap[-3] or closes[-4] < context.vwap[-4]):
            return

        if down_trend and highs[-1] - closes[-1] > closes[-1] - lows[-1]:
            return
        if up_trend and closes[-1] - lows[-1] > highs[-1] - closes[-1]:
            return

        for i in range(6, len(closes) - 7):
            close = closes[i]
            if close < np.min(closes[i - 6:i]) and close < np.min(closes[i + 1:i + 7]):
                levels.append(close)
            if close > np.max(closes[i - 6:i]) and close > np.max(closes[i + 1:i + 7]):
                levels.append(close)
        levels.sort()

        for i, level in enumerate(levels):
            if abs(closes[-3] - level) / level < 0.005:
                direction = 'long' if down_trend else 'short'
                action_type = ActionType.BUY_TO_OPEN if down_trend else ActionType.SELL_TO_OPEN
                take_profit = context.current_price * 1.01 if down_trend else context.current_price * 0.99
                stop_loss = None
                if down_trend:
                    for j in range(i + 1, len(levels)):
                        if levels[j] * 0.99 > context.current_price * 1.01:
                            take_profit = levels[j] * 0.99
                            break
                    stop_loss = levels[i] if levels[i] < context.current_price else context.current_price * 0.99
                if up_trend:
                    for j in range(i - 1, -1, -1):
                        if levels[j] * 1.01 < context.current_price * 0.99:
                            take_profit = levels[j] * 1.01
                            break
                    stop_loss = levels[i] if levels[i] > context.current_price else context.current_price * 1.01
                self._hold_positions[context.symbol] = {'stop_loss': stop_loss,
                                                        'take_profit': take_profit,
                                                        'direction': direction,
                                                        'entry_time': context.current_time,
                                                        'entry_price': context.current_price}
                return Action(context.symbol, action_type, 1, context.current_price)

    def _handle_position(self, context: Context) -> Optional[Action]:
        position = self._hold_positions[context.symbol]
        entry_time = position['entry_time']
        prev_close = context.intraday_lookback['Close'][-1]
        prev_open = context.intraday_lookback['Open'][-1]
        entry_price = position['entry_price']
        if position['direction'] == 'long':
            action = Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
            if context.current_price <= position['stop_loss'] or context.current_price >= position['take_profit']:
                self._hold_positions.pop(context.symbol)
                return action
            if prev_close < context.vwap[-1]:
                self._hold_positions.pop(context.symbol)
                return action
            if context.current_price > entry_price * 1.005 and prev_close < prev_open:
                return action
        else:
            action = Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)
            if context.current_price >= position['stop_loss'] or context.current_price <= position['take_profit']:
                self._hold_positions.pop(context.symbol)
                return action
            if prev_close > context.vwap[-1]:
                self._hold_positions.pop(context.symbol)
                return action
            if context.current_price < entry_price * 0.995 and prev_close > prev_open:
                return action
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            self._hold_positions.pop(context.symbol)
            return action


class ReversalProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> ReversalProcessor:
        return ReversalProcessor(lookback_start_date, lookback_end_date, data_source)
