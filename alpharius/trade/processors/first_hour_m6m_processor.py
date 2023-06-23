import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency, Position,
    ProcessorAction, DATETIME_TYPE, DAYS_IN_A_MONTH, DAYS_IN_A_QUARTER)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 20


class FirstHourM6mProcessor(Processor):

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

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if self.is_active(context.symbol):
            return self._close_position(context)
        elif context.symbol not in self._positions:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t != datetime.time(10, 0):
            return
        market_open_index = context.market_open_index
        intraday_highs = context.intraday_lookback['High'][market_open_index:]
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        interday_closes = context.interday_lookback['Close']
        if len(interday_closes) < DAYS_IN_A_QUARTER:
            return
        if interday_closes[-1] < 1.3 * interday_closes[-DAYS_IN_A_MONTH]:
            return
        if interday_closes[-DAYS_IN_A_MONTH] < 1.1 * interday_closes[-DAYS_IN_A_QUARTER]:
            return
        if interday_closes[-1] < np.max(interday_closes[-DAYS_IN_A_MONTH:]) * 0.8:
            return
        if intraday_closes[0] >= context.prev_day_close:
            return
        if len(intraday_highs) != 6:
            return
        current_gain = context.current_price / context.prev_day_close - 1
        if current_gain > context.l2h_avg:
            return
        for i in range(len(intraday_highs) - 1):
            if intraday_highs[i] > intraday_highs[i + 1] and intraday_closes[i] > intraday_closes[i + 1]:
                return
        self._positions[context.symbol] = {'status': 'pending', 'entry_time': context.current_time}
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Current gain: {current_gain * 100:.2f}%. L2h: {context.l2h_avg * 100:.2f}%. '
                           f'Current price {context.current_price}.')
        return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        if context.current_time >= position['entry_time'] + datetime.timedelta(minutes=20):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            self._positions.pop(context.symbol)
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class FirstHourM6mProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> FirstHourM6mProcessor:
        return FirstHourM6mProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
