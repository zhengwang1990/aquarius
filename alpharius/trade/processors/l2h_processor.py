import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, Mode, DAYS_IN_A_MONTH, DAYS_IN_A_YEAR, DATETIME_TYPE)
from ..data_loader import get_shortable_symbols
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 25
EXIT_TIME = datetime.time(16, 0)


class L2hProcessor(Processor):

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
        self._shortable_symbols = set(get_shortable_symbols())
        self._memo = dict()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != 'active']
        for symbol in to_remove:
            self._positions.pop(symbol)
        self._memo = dict()

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())) & self._shortable_symbols)

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _get_thresholds(self, context: Context) -> float:
        key = context.symbol + context.current_time.strftime('%F')
        if key in self._memo:
            return self._memo[key]
        interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
        interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
        l2h_gains = [h / l - 1 for h, l in zip(interday_highs, interday_lows)]
        l2h_avg = np.average(l2h_gains)
        threshold = l2h_avg * 0.75
        self._memo[key] = threshold
        return threshold

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t >= EXIT_TIME:
            return
        interday_closes = context.interday_lookback['Close']
        if len(interday_closes) < DAYS_IN_A_YEAR:
            return
        if (context.current_price < 1.2 * interday_closes[-DAYS_IN_A_MONTH] or
                context.current_price > interday_closes[-DAYS_IN_A_MONTH] * 2 or
                context.current_price > interday_closes[-DAYS_IN_A_YEAR] * 3):
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if len(intraday_closes) < 10:
            return
        if abs(context.current_price / context.prev_day_close - 1) > 0.5:
            return
        if context.current_price < np.max(intraday_closes):
            return
        for i in range(-1, -9, -1):
            if intraday_closes[i] <= intraday_closes[i - 1]:
                break
        else:
            return
        current_gain = context.current_price / intraday_closes[-10] - 1
        threshold = self._get_thresholds(context)
        is_trade = threshold < current_gain
        if is_trade or (context.mode == Mode.TRADE and current_gain > threshold * 0.8):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Current gain: {current_gain * 100:.2f}%. '
                               f'Threshold: {threshold * 100:.2f}%. '
                               f'Current price {context.current_price}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'active'}
            return ProcessorAction(context.symbol, ActionType.SELL_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        if position['status'] != 'active':
            return
        intraday_closes = context.intraday_lookback['Close']
        take_profit = (context.current_time == position['entry_time'] + datetime.timedelta(minutes=10) and
                       len(intraday_closes) >= 3 and intraday_closes[-1] < intraday_closes[-3])
        is_close = (take_profit or
                    context.current_time >= position['entry_time'] + datetime.timedelta(minutes=15) or
                    context.current_time.time() >= EXIT_TIME)
        if is_close:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            position['status'] = 'inactive'
            return ProcessorAction(context.symbol, ActionType.BUY_TO_CLOSE, 1)


class L2hProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> L2hProcessor:
        return L2hProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
