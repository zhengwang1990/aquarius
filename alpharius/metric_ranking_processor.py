from .common import *
from .constants import *
from typing import List
import logging
import numpy as np
import pandas as pd
import tabulate

NUM_HOLD_SYMBOLS = 3


class MetricRankingProcessor(Processor):

    def __init__(self, logging_enabled: bool) -> None:
        super().__init__()
        self._hold_positions = {}
        self._logging_enabled = logging_enabled
        self._nasdaq_100 = []
        self._prev_hold_positions = []

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.CLOSE_TO_CLOSE

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        self._nasdaq_100 = get_nasdaq100(view_time)
        stock_universe = list(set(self._nasdaq_100 + self._prev_hold_positions))
        return stock_universe

    def setup(self, hold_positions: List[Position]) -> None:
        self._hold_positions = {position.symbol: position
                                for position in hold_positions}
        self._prev_hold_positions = list(self._hold_positions.keys())

    def process_all_data(self, contexts: List[Context]) -> List[Action]:
        metrics = []
        volumes = []
        current_prices = {context.symbol: context.current_price for context in contexts}
        volume_factors = {}
        contexts_selected = [context for context in contexts if context.symbol in self._nasdaq_100]
        for context in contexts_selected:
            lookback_len = min(DAYS_IN_A_MONTH, len(context.interday_lookback))
            volume = np.dot(context.interday_lookback['VWAP'][-lookback_len:],
                            context.interday_lookback['Volume'][-lookback_len:])
            volumes.append((context.symbol, volume))
        volumes.sort(key=lambda s: s[1], reverse=True)
        for i, symbol in enumerate(volumes):
            volume_factors[symbol[0]] = 1.2 - 0.4 * i / len(volumes)
        for context in contexts_selected:
            metric = self._get_metric(context.interday_lookback,
                                      context.current_price,
                                      volume_factors[context.symbol])
            metrics.append((context.symbol, metric))
        metrics.sort(key=lambda s: s[1], reverse=True)
        if self._logging_enabled:
            metric_info = []
            for symbol, metric in metrics[:NUM_HOLD_SYMBOLS + 5]:
                price = current_prices[symbol]
                metric_info.append([symbol, price, metric])
            logging.info('Metric info\n' + tabulate.tabulate(
                metric_info, headers=['Symbol', 'Price', 'Metric'], tablefmt='grid'))
        new_symbols = [s[0] for s in metrics[:NUM_HOLD_SYMBOLS] if s[1] > 0]
        old_symbols = [symbol for symbol, position in self._hold_positions.items() if position.qty > 0]
        actions = []
        for symbol in old_symbols:
            if symbol not in new_symbols and symbol in current_prices:
                actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_prices[symbol]))
                self._hold_positions.pop(symbol)
        percent = max(1 / (1 + NUM_HOLD_SYMBOLS - len(new_symbols)), 0)
        for symbol in new_symbols:
            if symbol not in old_symbols:
                actions.append(Action(symbol, ActionType.BUY_TO_OPEN, percent, current_prices[symbol]))
        return actions

    @staticmethod
    def _get_metric(interday_lookback: pd.DataFrame, current_price: float, global_factor: float) -> float:
        if len(interday_lookback) < DAYS_IN_A_YEAR:
            return 0
        values = np.append(interday_lookback['Close'][-DAYS_IN_A_YEAR:], current_price)
        profits = [np.log(values[k + 1] / values[k]) for k in range(len(values) - 1)]
        r = np.average(profits)
        std = np.std(profits)
        for t in range(1, 11):
            if (profits[-t] - r) / std < -3:
                return 0
        metric = r * global_factor
        return metric


class MetricRankingProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> MetricRankingProcessor:
        return MetricRankingProcessor(logging_enabled)
