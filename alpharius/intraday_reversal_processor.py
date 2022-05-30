from .common import *
from .stock_universe import TopVolumeUniverse
from ta import momentum
from typing import List
import datetime
import numpy as np


class IntradayReversalProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._open_positions = set()
        self._stock_universe = TopVolumeUniverse(lookback_start_date, lookback_end_date, data_source,
                                                 num_stocks=100)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'intraday_reversal_processor.txt'),
                                      detail=True,
                                      name='intraday_reversal_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['TSLA', 'NVDA', 'AMAT']

    def setup(self, hold_positions: List[Position]) -> None:
        self._open_positions = set([position.symbol for position in hold_positions])

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._open_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        current_time = context.current_time.time()
        if current_time < datetime.time(11, 10) or current_time > datetime.time(15, 0):
            return
        interday_closes = context.interday_lookback['Close']
        if len(interday_closes) < 200 or context.current_price < np.average(interday_closes[-200:]):
            return
        intraday_closes = context.intraday_lookback['Close']
        if len(intraday_closes) < 20:
            return
        rsi = momentum.rsi(interday_closes[-6:], window=6)
        if rsi[-1] > 30:
            return
        mean = np.average(intraday_closes[-20:])
        std = np.std(intraday_closes[-20:])
        if context.current_price > mean - 2 * std:
            return
        # self._logger.debug('Enter long position of [%s].', context.symbol)
        self._open_positions.add(context.symbol)
        return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        intraday_closes = context.intraday_lookback['Close']
        mean = np.average(intraday_closes[-20:])
        std = np.std(intraday_closes[-20:])
        if context.current_price > mean + 2 * std or context.current_time.time() == datetime.time(16, 0):
            self._open_positions.remove(context.symbol)
            return Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)


class IntradayReversalProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> IntradayReversalProcessor:
        return IntradayReversalProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
