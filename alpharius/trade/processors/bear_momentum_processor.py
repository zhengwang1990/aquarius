import datetime
import os
from typing import List, Optional

import numpy as np
from ..common import (
    Action, ActionType, Context, Processor, ProcessorFactory, TradingFrequency,
    DATETIME_TYPE, DAYS_IN_A_MONTH, logging_config)

ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(14, 0)
N = {'TQQQ': 8, 'UCO': 9, 'FAS': 9}


class BearMomentumProcessor(Processor):
    """Momentum strategy that works in a bear market."""

    def __init__(self,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'bear_etf_processor.txt'),
                                      detail=True,
                                      name='bear_etf_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['TQQQ', 'UCO', 'FAS']

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        t = context.current_time.time()
        if t <= ENTRY_TIME or t >= EXIT_TIME:
            return
        market_open_ind = 0
        while context.intraday_lookback.index[market_open_ind].time() < datetime.time(9, 30):
            market_open_ind += 1
        intraday_closes = context.intraday_lookback['Close'][market_open_ind:]
        n = N.get(context.symbol, 8)
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
                               f'Up count [{up} / {n}]. Down count [{down} / {n}].')
        if down == n and context.current_price < context.prev_day_close:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'side': 'short'}
            return Action(context.symbol, ActionType.SELL_TO_OPEN, 1, context.current_price)
        if up == n and context.current_price > context.prev_day_close:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'side': 'long'}
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._positions[context.symbol]
        action_type = ActionType.SELL_TO_CLOSE if position[
            'side'] == 'long' else ActionType.BUY_TO_CLOSE
        action = Action(context.symbol, action_type, 1, context.current_price)
        if context.current_time < position['entry_time'] + datetime.timedelta(minutes=60):
            return
        self._positions.pop(context.symbol)
        return action


class BearMomentumProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               output_dir: str,
               *args, **kwargs) -> BearMomentumProcessor:
        return BearMomentumProcessor(output_dir)
