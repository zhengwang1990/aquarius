import datetime
import os
from typing import List, Optional, Tuple

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, Mode, DAYS_IN_A_MONTH, DATETIME_TYPE, logging_config)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 20
EXIT_TIME = datetime.time(16, 0)


class HourlyReversionProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date,
                                                               lookback_end_date,
                                                               data_source,
                                                               num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'hourly_reversion_processor.txt'),
                                      detail=True,
                                      name='hourly_reversion_processor')

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
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    @staticmethod
    def _get_thresholds(context: Context) -> Tuple[float, float]:
        interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
        interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
        h2l_losses = [l / h - 1 for h, l in zip(interday_highs, interday_lows)]
        h2l_avg = np.average(h2l_losses)
        h2l_std = np.std(h2l_losses)
        lower_threshold = max(h2l_avg - 3 * h2l_std, -0.5)
        upper_threshold = h2l_avg - 1 * h2l_std
        return lower_threshold, upper_threshold

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t >= EXIT_TIME:
            return
        market_open_index = context.market_open_index
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if len(intraday_closes) < 13:
            return
        if context.current_price > np.min(intraday_closes):
            return
        if abs(context.current_price / context.prev_day_close - 1) > 0.5:
            return
        hourly_loss = context.current_price / intraday_closes[-13] - 1
        lower_threshold, upper_threshold = self._get_thresholds(context)
        is_trade = lower_threshold < hourly_loss < upper_threshold
        if is_trade or (context.mode == Mode.TRADE and hourly_loss < upper_threshold * 0.8):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Hourly loss: {hourly_loss * 100:.2f}%. '
                               f'Threshold: {lower_threshold * 100:.2f}% ~ {upper_threshold * 100:.2f}%. '
                               f'Current price {context.current_price}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'active'}
            return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        if position['status'] != 'active':
            return
        intraday_closes = context.intraday_lookback['Close']
        index = -13 - (context.current_time - position['entry_time']).seconds // 300
        if len(intraday_closes) >= abs(index):
            loss = context.current_price / intraday_closes[index] - 1
            lower_threshold, _ = self._get_thresholds(context)
            if loss < lower_threshold:
                position['status'] = 'inactive'
                return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)
        if (context.current_time >= position['entry_time'] + datetime.timedelta(minutes=30) or
                context.current_time.time() >= EXIT_TIME):
            position['status'] = 'inactive'
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class HourlyReversionProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> HourlyReversionProcessor:
        return HourlyReversionProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
