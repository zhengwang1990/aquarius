from ..common import *
from typing import List
import datetime
import numpy as np

ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(14, 0)
N = 8


class TqqqProcessor(Processor):

    def __init__(self,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'tqqq_processor.txt'),
                                      detail=True,
                                      name='tqqq_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['TQQQ']

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
        if len(intraday_closes) < N + 1:
            return
        interday_closes = context.interday_lookback['Close'][-DAYS_IN_A_MONTH:]
        if len(interday_closes) < DAYS_IN_A_MONTH:
            return
        if context.current_price > np.max(interday_closes) * 0.7:
            return
        up, down = 0, 0
        intraday_high = context.intraday_lookback['High']
        intraday_low = context.intraday_lookback['Low']
        for i in range(-1, -N - 1, -1):
            if intraday_low[i] < intraday_low[i - 1]:
                down += 1
            if intraday_high[i] > intraday_high[i - 1]:
                up += 1
        if down == N:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'side': 'short'}
            return Action(context.symbol, ActionType.SELL_TO_OPEN, 1, context.current_price)
        if up == N:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'side': 'long'}
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._positions[context.symbol]
        action_type = ActionType.SELL_TO_CLOSE if position['side'] == 'long' else ActionType.BUY_TO_CLOSE
        action = Action(context.symbol, action_type, 1, context.current_price)
        if context.current_time < position['entry_time'] + datetime.timedelta(minutes=60):
            return
        self._positions.pop(context.symbol)
        return action


class TqqqProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               output_dir: str,
               *args, **kwargs) -> TqqqProcessor:
        return TqqqProcessor(output_dir)
