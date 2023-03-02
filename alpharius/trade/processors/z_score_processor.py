import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency, Position,
    ProcessorAction, Mode, DATETIME_TYPE, DAYS_IN_A_MONTH)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 20
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(16, 0)


class ZScoreProcessor(Processor):

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

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._memo = dict()

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _get_threshold(self, context: Context) -> float:
        key = context.symbol + context.current_time.strftime('%F')
        if key in self._memo:
            return self._memo[key]
        interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
        interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
        h2l_losses = [l / h - 1 for h, l in zip(interday_highs, interday_lows)]
        h2l_avg = np.average(h2l_losses)
        threshold = h2l_avg * 0.25
        self._memo[key] = threshold
        return threshold

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t <= ENTRY_TIME or t >= EXIT_TIME:
            return
        market_open_index = context.market_open_index
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        intraday_volumes = context.intraday_lookback['Volume'][market_open_index:]
        if len(intraday_closes) < 6:
            return
        if intraday_closes[-1] < context.prev_day_close < intraday_closes[-2]:
            return
        if context.current_price / context.prev_day_close > 2:
            return
        price_changes = [abs(intraday_closes[i] - intraday_closes[i - 1])
                         for i in range(1, len(intraday_closes))]
        z_price = (price_changes[-1] - np.mean(price_changes)) / (np.std(price_changes) + 1E-7)
        # Performance optimization. Skip unnecessary volume computation
        if z_price < 1.5:
            return
        z_volume = (intraday_volumes[-1] - np.mean(intraday_volumes)) / (np.std(intraday_volumes) + 1E-7)
        direction = 'up' if intraday_closes[-1] > intraday_closes[-2] else 'down'
        # In trade mode, the volume is slightly lower
        volume_threshold = 5.5 if context.mode == Mode.TRADE else 6
        if direction == 'up':
            threshold = 2.5
            is_trade = z_price > threshold and z_volume > volume_threshold
            is_logging = z_price > threshold - 1 and z_volume > 3
            if is_trade:
                p1 = price_changes[:-1]
                v1 = intraday_volumes[:-1]
                z1_price = (p1[-1] - np.mean(p1)) / (np.std(p1) + 1E-7)
                z1_volume = (v1[-1] - np.mean(v1)) / (np.std(v1) + 1E-7)
                is_trade = not (z1_price > threshold and z1_volume > 6)
        else:
            threshold = 2.5 if t < datetime.time(11, 0) else 3.5
            is_trade = z_price > threshold and z_volume < volume_threshold
            is_logging = z_price > threshold - 1
            if is_trade:
                threshold = self._get_threshold(context)
                current_loss = context.current_price / intraday_closes[-2] - 1
                is_trade = current_loss < threshold
                self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                                   f'Current loss: {current_loss * 100:.2f}%. '
                                   f'Threshold: {threshold * 100:.2f}%.')
        if is_trade or (context.mode == Mode.TRADE and is_logging):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Price z-score: {z_price:.2f}. Volume z-score: {z_volume:.2f}. '
                               f'Direction: {direction}. Current price {context.current_price}.')
        if not is_trade:
            return
        self._positions[context.symbol] = {'entry_time': context.current_time,
                                           'direction': direction}
        return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Closing position. Current price {context.current_price}')
        self._positions.pop(context.symbol)
        return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class ZScoreProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> ZScoreProcessor:
        return ZScoreProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
