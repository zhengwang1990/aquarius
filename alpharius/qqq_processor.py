from .common import *
from .data import HistoricalDataLoader
from .stock_universe import PrevThreeSigmaStockUniverse
from typing import List, Optional
import numpy as np


class QqqProcessor(Processor):

    def __init__(self,
                 data_source: DataSource,
                 logging_enabled: bool) -> None:
        super().__init__()
        self._data_loader = HistoricalDataLoader(TimeInterval.FIVE_MIN, data_source)
        self._hold = False
        self._trade_block = False
        self._logging_enabled = logging_enabled

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['QQQ']

    def setup(self, hold_positions: List[Position]) -> None:
        for position in hold_positions:
            if position.symbol == 'QQQ':
                self._hold = True
        self._trade_block = False

    def process_data(self, context: Context) -> Optional[Action]:
        closes = context.interday_lookback['Close']
        profits = [np.log(closes[i + 5] / closes[i]) for i in range(len(closes) - 5)]
        mean = np.mean(profits)
        std = np.std(profits)
        today_gain = np.log(context.current_price / closes[-5])
        if today_gain < mean - 2 * std:
            if self._hold:
                self._hold = False
                self._trade_block = True
                return Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
        if not self._hold and not self._trade_block:
            self._hold = True
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)


class QqqProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> QqqProcessor:
        return QqqProcessor(data_source, logging_enabled)
