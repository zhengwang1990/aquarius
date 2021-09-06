from .common import *
from .stock_universe import StockUniverse
import numpy as np


class SwingProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_universe = SwingStockUniverse(start_time=lookback_start_date,
                                                  end_time=lookback_end_date,
                                                  data_source=data_source)
        self._stock_universe.set_dollar_volume_filter(low=1E7, high=1E9)
        self._hold = False

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_universe.get_stock_universe(view_time)

    def process_data(self, context: Context) -> Optional[Action]:
        if self._hold:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if context.current_time.time() != datetime.time(16, 0):
            return
        self._hold = True
        return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        if context.current_time.time() != datetime.time(9, 35):
            return
        self._hold = False
        return Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)


class SwingProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> SwingProcessor:
        return SwingProcessor(lookback_start_date, lookback_end_date, data_source)


class SwingStockUniverse(StockUniverse):

    def __init__(self,
                 start_time: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__(start_time, end_time, data_source)

    def get_significant_drop(self, symbol: str, prev_day: DATETIME_TYPE) -> bool:
        hist = self._historical_data[symbol]
        p = timestamp_to_index(hist.index, prev_day)
        closes = np.array(hist['Close'][max(p - DAYS_IN_A_MONTH + 1, 1):p + 1])
        changes = np.array([np.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)
                            if closes[i + 1] > 0 and closes[i] > 0])
        if not len(changes):
            return False
        std = np.std(changes)
        mean = np.mean(changes)
        if std < 1E-7:
            return False
        if changes[-1] - mean < -3 * std:
            return False
        return True

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        symbols = super().get_stock_universe(view_time)
        res = []
        for symbol in symbols:
            if self.get_significant_drop(symbol, prev_day):
                res.append(symbol)
        return res

