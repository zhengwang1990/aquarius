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
        self._stock_unviverse.set_average_true_range_percent_filter(low=0.05)
        self._stock_unviverse.set_price_filer(low=5)
        self._hold_positions = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_unviverse.get_stock_universe(view_time)

    def handle_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._handle_position(context)
        if context.current_time.time() >= datetime.time(15, 55):
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
        if len(intraday_lookback) < 12:  # RSI size
            return
        levels = [context.prev_day_close]
        closes = intraday_lookback['Close']
        if np.abs(closes[-1] - closes[-2]) > np.abs(closes[-2] - closes[-3]):
            return
        up_trend, down_trend = False, False
        if closes[-1] > closes[-2] > closes[-3] > closes[-4] > closes[-5]:
            up_trend = True
        if closes[-1] < closes[-2] < closes[-3] < closes[-4] < closes[-5]:
            down_trend = True
        if not up_trend and not down_trend:
            return
        last_candle = intraday_lookback.iloc[-1]
        if down_trend and last_candle['Close'] - last_candle['Low'] < last_candle['High'] - last_candle['Close']:
            return
        if up_trend and last_candle['High'] - last_candle['Close'] < last_candle['Close'] - last_candle['Low']:
            return
        rsi = momentum.rsi(closes, window=12).values[-1]
        if down_trend and rsi > 20:
            return
        if up_trend and rsi < 80:
            return
        for i in range(6, len(closes) - 7):
            close = closes[i]
            if close < np.min(closes[i - 6:i]) and close < np.min(closes[i + 1:i + 7]):
                levels.append(close)
            if close > np.max(closes[i - 6:i]) and close > np.max(closes[i + 1:i + 7]):
                levels.append(close)
        levels.sort()
        for i, level in enumerate(levels):
            if abs(context.current_price - level) / level < 0.01:
                direction = 'long' if down_trend else 'short'
                action_type = ActionType.BUY_TO_OPEN if down_trend else ActionType.SELL_TO_OPEN
                take_profit = context.current_price * 1.01 if down_trend else context.current_price * 0.99
                stop_loss = context.current_price * 0.99 if down_trend else context.current_price * 1.01
                if down_trend:
                    for j in range(i + 1, len(levels)):
                        if levels[j] > context.current_price * 1.01:
                            take_profit = levels[j]
                            break
                if up_trend:
                    for j in range(i - 1, -1, -1):
                        if levels[j] < context.current_price * 0.99:
                            take_profit = levels[i - 1]
                            break
                self._hold_positions[context.symbol] = {'stop_loss': stop_loss,
                                                        'take_profit': take_profit,
                                                        'direction': direction,
                                                        'entry_time': context.current_time}
                return Action(context.symbol, action_type, 1, context.current_price)

    def _handle_position(self, context: Context) -> Optional[Action]:
        position = self._hold_positions[context.symbol]
        entry_time = position['entry_time']
        if position['direction'] == 'long':
            action = Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
            if context.current_price <= position['stop_loss'] or context.current_price >= position['take_profit']:
                return action
        else:
            action = Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)
            if context.current_price >= position['stop_loss'] or context.current_price <= position['take_profit']:
                return action
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
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
