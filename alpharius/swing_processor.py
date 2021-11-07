from .common import *
from .stock_universe import PrevThreeSigmaStockUniverse
from typing import List, Optional
import numpy as np


class SwingProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 logging_enabled: bool) -> None:
        super().__init__()
        self._stock_universe = PrevThreeSigmaStockUniverse(start_time=lookback_start_date,
                                                           end_time=lookback_end_date,
                                                           data_source=data_source)
        self._hold_positions = {}
        self.logging_enabled = logging_enabled
        self._prev_hold_positions = []

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.CLOSE_TO_OPEN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        universe = self._stock_universe.get_stock_universe(view_time) + list(self._prev_hold_positions) + ['TQQQ']
        return list(set(universe))

    def setup(self, hold_positions: List[Position] = ()) -> None:
        for position in hold_positions:
            if position.qty > 0:
                self._hold_positions[position.symbol] = {'side': 'long'}
        self._prev_hold_positions = list(self._hold_positions.keys())

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if context.current_time.time() != datetime.time(16, 0):
            return

        if context.symbol == 'TQQQ':
            self._hold_positions['TQQQ'] = {'side': 'long'}
            closes = context.interday_lookback['Close']
            daily_gain = max(context.current_price / closes[-1] - 1, 0)
            monthly_gain = max(context.current_price / closes[-DAYS_IN_A_MONTH] - 1, 0)
            percent = np.clip(1 - 10 * monthly_gain ** 2 - 25 * daily_gain ** 2, 0.2, 1)
            if self.logging_enabled:
                logging.info('Buying [TQQQ]. Current price [%f]', context.current_price)
            return Action(context.symbol, ActionType.BUY_TO_OPEN, percent, context.current_price)

        if context.symbol in self._prev_hold_positions:
            return

        interday_closes = context.interday_lookback['Close']
        today_change = context.current_price / interday_closes[-1] - 1
        if today_change > 0:
            if self.logging_enabled:
                logging.info('Skipping [%s]. Current price [%f]. today_change [%f] > 0 not satisfied.',
                             context.symbol, context.current_price, today_change)
            return
        yesterday_change = interday_closes[-2] / interday_closes[-1] - 1
        if yesterday_change > 0:
            if self.logging_enabled:
                logging.info('Skipping [%s]. Current price [%f]. yesterday_change [%f] > 0 not satisfied.',
                             context.symbol, context.current_price, yesterday_change)
            return
        if abs(today_change) > abs(yesterday_change) / 5:
            if self.logging_enabled:
                logging.info('Skipping [%s]. Current price [%f]. abs(today_change) [%f]'
                             '> abs(yesterday_change) / 5 [%f] not satisfied.',
                             context.symbol, context.current_price, abs(today_change), abs(yesterday_change) / 5)
            return
        if abs(today_change) > 0.05:
            return

        self._hold_positions[context.symbol] = {'side': 'long'}
        if self.logging_enabled:
            logging.info('Buying [%s]. Current price [%f].', context.symbol, context.current_price)
        return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        if context.current_time.time() < datetime.time(10, 0):
            return
        symbol = context.symbol
        position = self._hold_positions[symbol]
        side = position['side']
        assert side == 'long'
        self._hold_positions.pop(symbol)
        if self.logging_enabled:
            logging.info('Selling [%s]. Current price [%f].', context.symbol, context.current_price)
        return Action(symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)


class SwingProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> SwingProcessor:
        return SwingProcessor(lookback_start_date, lookback_end_date, data_source, logging_enabled)
