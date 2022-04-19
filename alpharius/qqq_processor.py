from .common import *
from .data import HistoricalDataLoader
from typing import List, Optional
import numpy as np


class QqqProcessor(Processor):

    def __init__(self,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._close_count = 0
        self._position = None
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'qqq_processor.txt'),
                                      detail=True,
                                      name='qqq_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['QQQ']

    def setup(self, hold_positions: List[Position]) -> None:
        self._close_count = 0
        self._position = None
        for position in hold_positions:
            if position.symbol == 'QQQ':
                self._position = {
                    'side': 'long' if position.qty > 0 else 'short',
                    'entry_time': position.entry_time,
                    'entry_price': position.entry_price,
                }

    def process_data(self, context: Context) -> Optional[Action]:
        if context.current_time.time() == datetime.time(9, 35):
            interday_close = context.interday_lookback['Close'][-DAYS_IN_A_MONTH:]
            interday_change = [interday_close[i + 1] / interday_close[i] - 1 for i in range(len(interday_close) - 1)]
            self._logger.debug('Std %s.', np.std(interday_change))

        if self._position is not None:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context):
        if context.current_time.time() > datetime.time(15, 30):
            return

        closes = context.intraday_lookback['Close']
        volumes = context.intraday_lookback['Volume']

        interday_close = context.interday_lookback['Close'][-DAYS_IN_A_MONTH:]
        interday_change = [interday_close[i + 1] / interday_close[i] - 1 for i in range(len(interday_close) - 1)]
        std = np.std(interday_change)
        if abs(context.current_price / closes[-2] - 1) < std:
            return

        if volumes[-1] < 2 * np.max(volumes[:-1]):
            return

        if closes[-1] > closes[-2]:
            self._position = {'side': 'long', 'entry_time': context.current_time, 'entry_price': context.current_price}
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)
        else:
            self._position = {'side': 'short', 'entry_time': context.current_time, 'entry_price': context.current_price}
            return Action(context.symbol, ActionType.SELL_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context):
        action = None
        side = self._position['side']
        entry_price = self._position['entry_price']
        self._close_count = (self._close_count + 1) % 2
        force_close = self._close_count == 0
        if side == 'long':
            if force_close or context.current_price > entry_price:
                action = Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
        else:
            if force_close or context.current_price < entry_price:
                action = Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)
        if action is not None:
            self._position = None
            self._close_count = 0
        return action


class QqqProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> QqqProcessor:
        return QqqProcessor(data_source, output_dir)
