from .common import *
from .stock_universe import PrevThreeSigmaStockUniverse
from typing import Any, Dict, List, Optional


class SwingProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__()
        self._stock_universe = PrevThreeSigmaStockUniverse(start_time=lookback_start_date,
                                                           end_time=lookback_end_date,
                                                           data_source=data_source)
        self._hold_positions = {}
        self._prev_hold_positions = []

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        universe = self._stock_universe.get_stock_universe(view_time) + list(self._hold_positions.keys()) + ['TQQQ']
        return list(set(universe))

    def setup(self, hold_positions: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        if hold_positions is not None:
            self._hold_positions = hold_positions
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
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

        if context.symbol in self._prev_hold_positions:
            return

        interday_closes = context.interday_lookback['Close']
        today_change = context.current_price / interday_closes[-1] - 1
        if today_change > 0:
            return

        yesterday_change = interday_closes[-2] / interday_closes[-1] - 1
        if today_change * yesterday_change < 0:
            return
        if abs(today_change) > abs(yesterday_change) / 5:
            return
        if abs(today_change) > 0.05:
            return

        self._hold_positions[context.symbol] = {'side': 'long'}
        return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        if context.current_time.time() < datetime.time(10, 0):
            return
        symbol = context.symbol
        position = self._hold_positions[symbol]
        side = position['side']
        assert side == 'long'
        self._hold_positions.pop(symbol)
        return Action(symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)


class SwingProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> SwingProcessor:
        return SwingProcessor(lookback_start_date, lookback_end_date, data_source)
