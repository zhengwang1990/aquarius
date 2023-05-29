import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, Mode, DATETIME_TYPE)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 20
N_LONG = 6


def _round_num(num: float):
    magnitude = 10 ** (np.round(np.log10(num)) - 1)
    return np.round(num / magnitude) * magnitude


class CrossCloseProcessor(Processor):
    """Strategy acting on 5-min bar crossing previous day close."""

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__(output_dir)
        self._positions = dict()
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date,
                                                               lookback_end_date,
                                                               data_source,
                                                               num_stocks=NUM_UNIVERSE_SYMBOLS)

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != 'active']
        for symbol in to_remove:
            self._positions.pop(symbol)

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if self.is_active(context.symbol):
            return self._close_position(context)
        elif context.symbol not in self._positions:
            action = self._open_short_position(context)
            if not action:
                action = self._open_long_position(context)
            return action

    def _open_short_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if not (t < datetime.time(10, 0) or
                datetime.time(10, 30) <= t < datetime.time(11, 0)):
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        intraday_opens = context.intraday_lookback['Open'][market_open_index:]
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if len(intraday_closes) < 3:
            return
        if abs(context.current_price / context.prev_day_close - 1) > 0.5:
            return
        if context.current_price > intraday_closes[-2]:
            return
        prev_loss = intraday_closes[-2] / intraday_closes[-3] - 1
        threshold = context.h2l_avg * 0.45
        is_cross = intraday_opens[-2] > context.prev_day_close > intraday_closes[-1]
        is_trade = prev_loss < threshold and is_cross
        if is_trade or (context.mode == Mode.TRADE and prev_loss < threshold * 0.8 and is_cross):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Prev loss: {prev_loss * 100:.2f}%. '
                               f'Threshold: {threshold * 100:.2f}%. '
                               f'Current price {context.current_price}. '
                               'Side: short')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'pending',
                                               'side': 'short'}
            return ProcessorAction(context.symbol, ActionType.SELL_TO_OPEN, 1)

    def _open_long_position(self, context: Context) -> Optional[ProcessorAction]:
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if len(intraday_closes) < N_LONG + 1:
            return
        level = None
        if intraday_closes[-2] < context.prev_day_close < intraday_closes[-1]:
            level = context.prev_day_close
        elif intraday_closes[-2] < _round_num(context.current_price) < intraday_closes[-1]:
            level = _round_num(context.current_price)
        if level is None:
            return
        for i in range(-N_LONG, 0):
            if intraday_closes[i] < intraday_closes[i - 1]:
                return
        if context.current_price != np.max(intraday_closes):
            return
        if intraday_closes[-N_LONG] > 0.6 * np.max(intraday_closes) + 0.4 * np.min(intraday_closes):
            return
        intraday_opens = context.intraday_lookback['Open'][market_open_index:]
        for i in range(len(intraday_closes) - N_LONG):
            if intraday_opens[i] < level < intraday_closes[i]:
                break
        else:
            return
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Level: {level}. '
                           f'Current price: {context.current_price}. Side: long.')
        self._positions[context.symbol] = {'entry_time': context.current_time,
                                           'status': 'active',
                                           'side': 'long'}
        return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        side = position['side']
        if side == 'short':
            intraday_closes = context.intraday_lookback['Close']
            take_profit = (context.current_time == position['entry_time'] + datetime.timedelta(minutes=5)
                           and context.current_price < intraday_closes[-2])
            is_close = (take_profit or
                        context.current_time >= position['entry_time'] + datetime.timedelta(minutes=10) or
                        context.current_time.time() >= datetime.time(16, 0))
        else:
            is_close = (context.current_time >= position['entry_time'] + datetime.timedelta(minutes=60)
                        or context.current_time.time() >= datetime.time(16, 0))
        if is_close:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            position['status'] = 'inactive'
            action_type = ActionType.BUY_TO_CLOSE if side == 'short' else ActionType.SELL_TO_CLOSE
            return ProcessorAction(context.symbol, action_type, 1)


class CrossCloseProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> CrossCloseProcessor:
        return CrossCloseProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
