from .common import *
from .constants import *
from .stock_universe import StockUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 100
NUM_DIRECTIONAL_SYMBOLS = 5


class MovingMomentumProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 logging_enabled: bool) -> None:
        super().__init__()
        self._stock_universe = MovingMomentumStockUniverse(lookback_start_date, lookback_end_date, data_source)
        self._logging_enabled = logging_enabled
        self._universe_symbols = []
        self._hold_positions = dict()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        hold_symbols = list(self._hold_positions.keys())
        self._universe_symbols = self._stock_universe.get_stock_universe(view_time)
        return list(set(hold_symbols + self._universe_symbols))

    def process_all_data(self, contexts: List[Context]) -> List[Action]:
        if not contexts:
            return []
        context0 = contexts[0]
        current_prices = {context.symbol: context.current_price for context in contexts}
        actions = []
        if context0.current_time.time() >= datetime.time(16, 0):
            for symbol in self._hold_positions:
                if symbol in current_prices:
                    actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_prices[symbol]))
            self._hold_positions.clear()
            return actions
        if context0.current_time.time() < datetime.time(10, 0):
            return []
        if context0.current_time.time() > datetime.time(10, 0):
            return self._stop_loss(contexts)
        performances = []
        for context in contexts:
            if context.symbol in self._universe_symbols and context.current_price < context.prev_day_close:
                performances.append((context.symbol, self._get_performance(context)))
        performances.sort(key=lambda s: s[1])
        long_symbols = [s[0] for s in performances[-NUM_DIRECTIONAL_SYMBOLS:] if s[1] > 0]
        for symbol in list(self._hold_positions):
            if symbol not in long_symbols and symbol in current_prices:
                self._hold_positions.pop(symbol)
                actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_prices[symbol]))
        for symbol in long_symbols:
            if symbol not in self._hold_positions:
                entry_price = current_prices[symbol]
                self._hold_positions[symbol] = {'entry_price': entry_price, 'side': 'long'}
                actions.append(Action(symbol, ActionType.BUY_TO_OPEN, 1, current_prices[symbol]))
        return actions

    @staticmethod
    def _get_performance(context: Context) -> float:
        interday_lookback = context.interday_lookback
        if len(interday_lookback) < DAYS_IN_A_YEAR:
            return 0
        opens = interday_lookback['Open'][-DAYS_IN_A_YEAR:]
        closes = interday_lookback['Close'][-DAYS_IN_A_YEAR:]
        intraday_returns = []
        for open_price, close_price in zip(opens, closes):
            intraday_returns.append(np.log(close_price / open_price))
            intraday_returns.sort()
        performance = float(np.sum(intraday_returns[DAYS_IN_A_MONTH:-DAYS_IN_A_MONTH]))
        performance -= 2 * np.log(context.current_price / closes[-1])
        return performance

    def _stop_loss(self, contexts: List[Context]) -> List[Action]:
        actions = []
        for context in contexts:
            symbol = context.symbol
            if symbol not in self._hold_positions:
                continue
            entry_price = self._hold_positions[symbol]['entry_price']
            if context.current_price < 0.99 * entry_price:
                self._hold_positions.pop(symbol)
                actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price))
        return actions


class MovingMomentumProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> MovingMomentumProcessor:
        return MovingMomentumProcessor(lookback_start_date, lookback_end_date, data_source, logging_enabled)


class MovingMomentumStockUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        self._stock_symbols = set(COMPANY_SYMBOLS)

    def get_stock_universe_impl(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        dollar_volumes = []
        for symbol, hist in self._historical_data.items():
            if symbol not in self._stock_symbols:
                continue
            if prev_day not in hist.index:
                continue
            prev_day_ind = timestamp_to_index(hist.index, prev_day)
            if prev_day_ind < DAYS_IN_A_MONTH:
                continue
            prev_close = hist['Close'][prev_day_ind]
            if prev_close < 5:
                continue
            dollar_volume = self._get_dollar_volume(symbol, prev_day_ind)
            if dollar_volume < 1E7:
                continue
            dollar_volumes.append((symbol, dollar_volume))
        dollar_volumes.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in dollar_volumes[500:600]]
