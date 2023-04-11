import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ProcessorAction, ActionType, Context, Processor, ProcessorFactory, TradingFrequency,
    DataSource, DATETIME_TYPE, DAYS_IN_A_MONTH)
from ..stock_universe import IntradayVolatilityStockUniverse

ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(14, 0)
NUM_STOCKS = 15
CONFIG = {'TQQQ': 8, 'UCO': 9, 'FAS': 9, 'NUGT': 9}
OTHER_N = 11


class BearMomentumProcessor(Processor):
    """Momentum strategy that works in a bear market."""

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
                                                               num_stocks=NUM_STOCKS)

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(CONFIG.keys()) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t <= ENTRY_TIME or t >= EXIT_TIME:
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        n = CONFIG.get(context.symbol, OTHER_N)
        if len(intraday_closes) < n + 1:
            return
        interday_closes = context.interday_lookback['Close'][-DAYS_IN_A_MONTH * 2:]
        if len(interday_closes) < DAYS_IN_A_MONTH * 2:
            return
        if context.current_price > np.max(interday_closes) * 0.7:
            return
        up, down = 0, 0
        intraday_high = context.intraday_lookback['High']
        intraday_low = context.intraday_lookback['Low']
        for i in range(-1, -n - 1, -1):
            if intraday_low[i] < intraday_low[i - 1]:
                down += 1
            if intraday_high[i] > intraday_high[i - 1]:
                up += 1
        if up >= n - 2 or down >= n - 2:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Up count [{up} / {n}]. Down count [{down} / {n}]. '
                               f'Current price {context.current_price}.')
        if down == n and context.current_price < context.prev_day_close:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'side': 'short'}
            return ProcessorAction(context.symbol, ActionType.SELL_TO_OPEN, 1)
        if up == n and context.current_price > context.prev_day_close:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'side': 'long'}
            return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        def _exit_action():
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            self._positions.pop(context.symbol)
            return action

        position = self._positions[context.symbol]
        action_type = ActionType.SELL_TO_CLOSE if position['side'] == 'long' else ActionType.BUY_TO_CLOSE
        action = ProcessorAction(context.symbol, action_type, 1)
        wait_minutes = 60 if context.symbol in CONFIG else 90
        if context.current_time >= position['entry_time'] + datetime.timedelta(minutes=wait_minutes):
            return _exit_action()
        intrayday_closes = context.intraday_lookback['Close']
        if (context.symbol not in CONFIG and
                position['side'] == 'long' and
                len(intrayday_closes) >= 2 and
                intrayday_closes[-2] < context.prev_day_close and
                context.current_price < context.prev_day_close):
            return _exit_action()


class BearMomentumProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> BearMomentumProcessor:
        return BearMomentumProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
