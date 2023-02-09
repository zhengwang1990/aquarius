import datetime
from typing import List, Optional, Tuple

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, Mode, DAYS_IN_A_MONTH, DATETIME_TYPE)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 20
EXIT_TIME = datetime.time(16, 0)
# 3 hours only works if 1 hour and 2 hours are not triggered
PARAMS = [(10, 1), (13, 1), (25, 1.75), (37, 2.25)]


class H2lHourProcessor(Processor):

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
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _get_h2l_stats(self, context: Context) -> Tuple[float, float, float]:
        key = context.symbol + context.current_time.strftime('%F')
        if key in self._memo:
            return self._memo[key]
        interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
        interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
        h2l_losses = [l / h - 1 for h, l in zip(interday_highs, interday_lows)]
        h2l_avg = float(np.average(h2l_losses))
        h2l_std = float(np.std(h2l_losses))
        lower_threshold = max(h2l_avg - 3 * h2l_std, -0.5)
        res = (lower_threshold, h2l_avg, h2l_std)
        self._memo[key] = res
        return res

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t >= EXIT_TIME:
            return
        interday_closes = context.interday_lookback['Close']
        # Avoid short squeeze caused by retail trader
        if max(interday_closes[-1], context.current_price) / interday_closes[-5] > 4:
            return
        market_open_index = context.market_open_index
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if context.current_price > np.min(intraday_closes):
            return
        if abs(context.current_price / context.prev_day_close - 1) > 0.5:
            return
        intraday_opens = context.intraday_lookback['Open'][market_open_index:]
        if intraday_opens[-1] > context.prev_day_close > intraday_closes[-1]:
            return
        lower_threshold, h2l_avg, h2l_std = self._get_h2l_stats(context)
        for n, z in PARAMS:
            if len(intraday_closes) < n:
                continue
            current_loss = context.current_price / intraday_closes[-n] - 1
            upper_threshold = h2l_avg - z * h2l_std
            is_trade = lower_threshold < current_loss < upper_threshold
            if is_trade or (context.mode == Mode.TRADE and current_loss < upper_threshold * 0.8):
                self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                                   f'Current loss: {current_loss * 100:.2f}%. N: {n}. '
                                   f'Threshold: {lower_threshold * 100:.2f}% ~ {upper_threshold * 100:.2f}%. '
                                   f'Current price {context.current_price}.')
            if is_trade:
                self._positions[context.symbol] = {'entry_time': context.current_time,
                                                   'status': 'active', 'n': n}
                return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        if position['status'] != 'active':
            return
        intraday_closes = context.intraday_lookback['Close']
        index = -position['n'] - (context.current_time - position['entry_time']).seconds // 300
        stop_loss = False
        if len(intraday_closes) >= abs(index):
            current_loss = context.current_price / intraday_closes[index] - 1
            lower_threshold, _, _ = self._get_h2l_stats(context)
            stop_loss = current_loss < lower_threshold
        if (stop_loss or
                context.current_time >= position['entry_time'] + datetime.timedelta(minutes=35) or
                context.current_time.time() >= EXIT_TIME):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            position['status'] = 'inactive'
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class H2lHourProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> H2lHourProcessor:
        return H2lHourProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
