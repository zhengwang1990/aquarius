from alpharius.common import *
from alpharius.stock_universe import IntradayRangeStockUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 100
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(16, 0)


class IntradayMomentumProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._stock_universe = IntradayRangeStockUniverse(lookback_start_date,
                                                          lookback_end_date,
                                                          data_source,
                                                          num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'intraday_momentum_processor.txt'),
                                      detail=True,
                                      name='intraday_momentum_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._positions = {
            position.symbol: {'side': 'long' if position.qty > 0 else 'short', 'entry_time': position.entry_time}
            for position in hold_positions
        }

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context):
        if context.current_time.time() <= ENTRY_TIME or context.current_time.time() >= datetime.time(15, 50):
            return
        intraday_closes = context.intraday_lookback['Close']
        if len(intraday_closes) < 6:
            return
        intraday_volumes = context.intraday_lookback['Volume']
        price_changes = [abs(intraday_closes[i] - intraday_closes[i - 1]) for i in range(1, len(intraday_closes))]
        if price_changes[-1] < np.mean(price_changes) + 4 * np.std(price_changes):
            return
        if intraday_volumes[-1] < np.mean(intraday_volumes) + 4 * np.std(intraday_volumes):
            return
        if intraday_closes[-1] > intraday_closes[-2]:
            side = 'long'
            action_type = ActionType.BUY_TO_OPEN
        else:
            return
            side = 'short'
            action_type = ActionType.SELL_TO_OPEN

        self._positions[context.symbol] = {'entry_time': context.current_time, 'side': side}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context):
        current_time = context.current_time
        position = self._positions[context.symbol]
        if (current_time.time() < EXIT_TIME
                and context.current_time < position['entry_time'] + datetime.timedelta(minutes=5)):
            return
        if position['side'] == 'long':
            action = Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
        else:
            action = Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)
        self._positions.pop(context.symbol)
        return action


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
