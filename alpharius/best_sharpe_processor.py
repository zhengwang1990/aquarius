from .common import *
from .constants import *
from .stock_universe import StockUniverse
from typing import List
import numpy as np


def _get_sharpe_raio(interday_lookback: pd.DataFrame, current_price: float) -> float:
    values = np.append(interday_lookback['Close'], current_price)
    profits = [np.log(values[k + 1] / values[k]) for k in range(len(values) - 1)]
    r = np.average(profits)
    return r
    #std = np.std(profits)
    #sharpe_ratio = r / std
    #return sharpe_ratio


class BestSharpeProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 logging_enabled: bool) -> None:
        super().__init__()
        self._hold_positions = {}
        self.logging_enabled = logging_enabled
        self._stock_universe = StockUniverse(history_start=lookback_start_date,
                                             end_time=lookback_end_date,
                                             data_source=data_source)
        self._stock_universe.set_price_filer(low=5)
        self._stock_universe.set_dollar_volume_filter(low=1E6, high=1E8)
        self._prev_hold_positions = []

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.CLOSE_TO_CLOSE

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return NASDAQ100_SYMBOLS
        #return self._stock_universe.get_stock_universe(view_time) + self._prev_hold_positions

    def setup(self, hold_positions: List[Position] = ()) -> None:
        for position in hold_positions:
            if position.qty > 0:
                self._hold_positions[position.symbol] = {'side': 'long'}
            else:
                self._hold_positions[position.symbol] = {'side': 'short'}
        self._prev_hold_positions = list(self._hold_positions.keys())

    def process_all_data(self, contexts: List[Context]) -> List[Action]:
        sharpe_ratios = []
        current_prices = {}
        for context in contexts:
            sharpe_ratio = _get_sharpe_raio(context.interday_lookback, context.current_price)
            sharpe_ratios.append((context.symbol, sharpe_ratio))
            current_prices[context.symbol] = context.current_price
        sharpe_ratios.sort(key=lambda s: s[1], reverse=True)
        new_long_symbols = [s[0] for s in sharpe_ratios[:10]]
        old_long_symbols = [symbol for symbol, info in self._hold_positions.items() if info['side'] == 'long']
        new_short_symbols = [s[0] for s in sharpe_ratios[-10:]]
        old_short_symbols = [symbol for symbol, info in self._hold_positions.items() if info['side'] == 'short']
        actions = []
        for symbol in old_long_symbols:
            if symbol not in new_long_symbols and symbol in current_prices:
                actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_prices[symbol]))
                self._hold_positions.pop(symbol)
        for symbol in new_long_symbols:
            if symbol not in old_long_symbols:
                actions.append(Action(symbol, ActionType.BUY_TO_OPEN, 1, current_prices[symbol]))
                self._hold_positions[symbol] = {'side': 'long'}
        # for symbol in old_short_symbols:
        #     if symbol not in new_short_symbols and symbol in current_prices:
        #         actions.append(Action(symbol, ActionType.BUY_TO_CLOSE, 1, current_prices[symbol]))
        #         self._hold_positions.pop(symbol)
        # for symbol in new_short_symbols:
        #     if symbol not in old_short_symbols:
        #         actions.append(Action(symbol, ActionType.SELL_TO_OPEN, 1, current_prices[symbol]))
        #         self._hold_positions[symbol] = {'side': 'short'}

        return actions


class BestSharpeProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> BestSharpeProcessor:
        return BestSharpeProcessor(lookback_start_date, lookback_end_date, data_source, logging_enabled)
