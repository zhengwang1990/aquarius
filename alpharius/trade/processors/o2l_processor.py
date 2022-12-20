import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, Mode, DAYS_IN_A_MONTH, DATETIME_TYPE)
from ..stock_universe import MonthlyGainStockUniverse

NUM_UNIVERSE_SYMBOLS = 15
EXIT_TIME = datetime.time(13, 0)


class O2lProcessor(Processor):
    """Open to low processor predicts intraday lows based on market open prices."""

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__(output_dir)
        self._positions = dict()
        self._stock_universe = MonthlyGainStockUniverse(lookback_start_date,
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
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    @staticmethod
    def _get_thresholds(context):
        interday_opens = context.interday_lookback['Open'][-DAYS_IN_A_MONTH:]
        interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
        o2l_losses = [l / o - 1 for o, l in zip(interday_opens, interday_lows)]
        o2l_avg = np.average(o2l_losses)
        o2l_std = np.std(o2l_losses)
        upper_threshold = o2l_avg - 4 * o2l_std
        lower_threshold = max(o2l_avg - 6 * o2l_std, -0.4)
        return lower_threshold, upper_threshold

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t >= EXIT_TIME:
            return
        market_open_index = context.market_open_index
        market_open_price = context.intraday_lookback['Open'][market_open_index]
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if intraday_closes[-1] > np.min(intraday_closes):
            return
        current_loss = context.current_price / market_open_price - 1
        lower_threshold, upper_threshold = self._get_thresholds(context)
        is_trade = lower_threshold < current_loss < upper_threshold
        if is_trade or (context.mode == Mode.TRADE and current_loss < upper_threshold * 0.8):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Current loss: {current_loss * 100:.2f}%. '
                               f'Threshold: {lower_threshold * 100:.2f}% ~ {upper_threshold * 100:.2f}%. '
                               f'Current price: {context.current_price}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'active'}
            return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        if position['status'] != 'active':
            return
        if (context.current_time >= position['entry_time'] + datetime.timedelta(minutes=15) or
                context.current_time.time() >= EXIT_TIME):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            position['status'] = 'inactive'
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class O2lProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> O2lProcessor:
        return O2lProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
