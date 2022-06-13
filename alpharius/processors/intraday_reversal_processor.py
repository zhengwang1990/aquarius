from alpharius.common import *
from alpharius.stock_universe import IntradayRangeStockUniverse
from typing import List
import datetime
import numpy as np

N_TD = 9
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(16, 0)


class IntradayReversalProcessor(Processor):

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
                                                          data_source,
                                                          num_stocks=50)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'intraday_reversal_processor.txt'),
                                      detail=True,
                                      name='intraday_reversal_processor')
        self._intraday_history = set()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        [position.symbol for position in self._interday_positions]))

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._interday_positions = hold_positions
        self._intraday_history.clear()

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._intraday_positions:
            return self._close_position(context)
        if context.symbol in self._intraday_history:
            return
        current_time = context.current_time.time()
        if current_time < ENTRY_TIME or current_time > datetime.time(15, 0):
            return
        interday_closes = context.interday_lookback['Close']
        if context.current_price < np.average(interday_closes[-200:]):
            return
        closes = context.intraday_lookback['Close']
        volumes = context.intraday_lookback['Volume']
        if context.current_price > context.vwap[-1]:
            return
        if len(closes) < N_TD + 3:
            return
        for i in range(-N_TD, -1):
            if closes[i] >= closes[i - 3]:
                return
        v1 = np.average(volumes[-N_TD:-N_TD // 3 * 2])
        v2 = np.average(volumes[-N_TD // 3 * 2: -N_TD // 3])
        v3 = np.average(volumes[-N_TD // 3:])
        if not 0.5 * v1 > 0.75 * v2 > v3:
            return
        if closes[-1] < closes[-2]:
            return
        self._intraday_positions[context.symbol] = {'side': 'long',
                                                    'entry_price': context.current_price,
                                                    'entry_time': context.current_time}
        return Action(context.symbol, ActionType.BUY_TO_OPEN, 0.5, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._intraday_positions[context.symbol]
        current_time = context.current_time
        if current_time.time() >= EXIT_TIME or current_time >= position['entry_time'] + datetime.timedelta(hours=1):
            self._intraday_positions.pop(context.symbol)
            self._intraday_history.add(context.symbol)
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
