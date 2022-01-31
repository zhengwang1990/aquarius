from .common import *
from .stock_universe import TopVolumeUniverse, IntradayRangeStockUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 100
NUM_DIRECTIONAL_SYMBOLS = 5
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(15, 30)


class IntradayMomentumProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._interday_positions = []
        self._intraday_positions = dict()
        self._stock_universe = IntradayRangeStockUniverse(lookback_start_date,
                                                          lookback_end_date,
                                                          data_source)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'intraday_momentum_processor.txt'),
                                      detail=True,
                                      name='intraday_momentum_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        [position.symbol for position in self._interday_positions]))
        # return ['SPY']

    def setup(self, hold_positions: List[Position]) -> None:
        self._interday_positions = hold_positions

    def process_data(self, context: Context) -> Optional[Action]:
        if context.current_time.time() == datetime.time(15, 30):
            prev_close = context.prev_day_close
            intraday_lookback = context.intraday_lookback
            c1 = self.get_price_at_time(intraday_lookback, datetime.time(9, 55))
            c2 = self.get_price_at_time(intraday_lookback, datetime.time(14, 55))
            c3 = context.current_price
            true_range = self.get_true_range(context.interday_lookback)
            if c1 is None or c2 is None:
                return None
            if abs(c3 / prev_close - 1) < 2 * true_range:
                return None
            if c1 > prev_close and c3 > c2:
                self._intraday_positions[context.symbol] = {'side': 'long'}
                return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)
        if context.current_time.time() == datetime.time(16, 0):
            if context.symbol in self._intraday_positions:
                if self._intraday_positions[context.symbol]['side'] == 'long':
                    return Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
        return None

    @staticmethod
    def get_price_at_time(intraday_lookback, t):
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() == t:
                return intraday_lookback['Close'][i]
        return None

    @staticmethod
    def get_true_range(interday_lookback):
        atrp = []
        if len(interday_lookback) < DAYS_IN_A_YEAR:
            return 0
        for i in range(-DAYS_IN_A_YEAR + 1, -1):
            h = interday_lookback['High'][i]
            l = interday_lookback['Low'][i]
            c = interday_lookback['Close'][i - 1]
            atrp.append(max(h - l, h - c, c - l) / c)
        return np.average(atrp) if atrp else 0


class IntradayMomentumProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> IntradayMomentumProcessor:
        return IntradayMomentumProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
