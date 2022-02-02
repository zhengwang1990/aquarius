from .common import *
from .stock_universe import IntradayRangeStockUniverse
from typing import List
import datetime
import numpy as np

N_TD = 15
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(15, 30)


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
                                                          num_stocks=20)
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

    def setup(self, hold_positions: List[Position]) -> None:
        self._interday_positions = hold_positions
        self._intraday_history.clear()

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._intraday_positions:
            return self._close_position(context)
        if context.symbol in self._intraday_history:
            return

        current_time = context.current_time.time()
        if current_time < datetime.time(10, 30) or current_time > datetime.time(15, 0):
            return
        interday_closes = context.interday_lookback['Close']
        if context.current_price < interday_closes[-5]:
            return
        closes = context.intraday_lookback['Close']
        lows = context.intraday_lookback['Low']
        opens = context.intraday_lookback['Open']
        volumes = context.intraday_lookback['Volume']
        if len(closes) < N_TD + 4:
            return
        for i in range(-N_TD, 0):
            if closes[i] >= closes[i - 4]:
                return
        for i in range(-2, 0):
            if lows[i] >= np.min(lows[-4:-2]):
                return
        if closes[-1] < opens[-1]:
            return
        if volumes[-1] < volumes[-2]:
            return
        take_profit = np.max(closes)
        stop_loss = np.min(lows[-20:])
        self._intraday_positions[context.symbol] = {'side': 'long', 'entry_price': context.current_price,
                                                    'entry_time': current_time, 'take_profit': take_profit,
                                                    'stop_loss': stop_loss}
        return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._intraday_positions[context.symbol]
        if (context.current_price >= position['take_profit'] or context.current_price <= position['stop_loss']
                or context.current_time.time() >= datetime.time(15, 30)):
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
