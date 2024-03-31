import datetime
from typing import List, Optional

import numpy as np

from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency, Position,
    ProcessorAction, DATETIME_TYPE)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 20
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(16, 0)


class OpenHighProcessor(Processor):

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

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != 'active']
        for symbol in to_remove:
            self._positions.pop(symbol)

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if self.is_active(context.symbol):
            return self._close_position(context)
        elif context.symbol not in self._positions:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if not ENTRY_TIME <= t < EXIT_TIME:
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        interday_closes = context.interday_lookback['Close'].tolist()
        if interday_closes[-1] < np.min(interday_closes[-20:]) * 1.4:
            return
        intraday_opens = context.intraday_lookback['Open'].tolist()[market_open_index:]
        open_price = intraday_opens[0]
        open_gain = open_price / context.prev_day_close - 1
        if open_gain < context.l2h_avg:
            return
        if context.current_price < context.prev_day_close:
            return
        intraday_closes = context.intraday_lookback['Close'].tolist()[market_open_index:]
        n = 4
        if len(intraday_closes) < n:
            return
        for i in range(-1, -n - 1, -1):
            if intraday_closes[i] >= intraday_opens[i]:
                return
        drop = context.current_price / intraday_opens[-n] - 1
        threshold = 1.3 * context.h2l_avg
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Current drop: {drop * 100:.2f}%. Drop threshold: {threshold * 100:.2f}%. '
                           f'Current price: {context.current_price}.')
        if drop > threshold:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'pending'}
            return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        stop_loss = context.current_price < context.prev_day_close
        is_close = (stop_loss or
                    context.current_time >= position['entry_time'] + datetime.timedelta(minutes=15)
                    or context.current_time.time() >= EXIT_TIME)
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Closing position: {is_close}. Current price {context.current_price}.')
        if is_close:
            position['status'] = 'inactive'
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class OpenHighProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> OpenHighProcessor:
        return OpenHighProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
