from .common import *
from .constants import *
from typing import List
import logging
import numpy as np
import pandas as pd
import tabulate

NUM_HOLD_SYMBOLS = 10


def _get_metric(interday_lookback: pd.DataFrame, current_price: float, global_factor: float) -> float:
    values = np.append(interday_lookback['Close'], current_price)
    for t in [1, 3, 5]:
        pt = [np.log(values[k + t] / values[k]) for k in range(len(values) - t)]
        if abs(pt[-1] - np.average(pt)) / np.std(pt) > 3:
            return 0
    profits = [np.log(values[k + 1] / values[k]) for k in range(len(values) - 1)]
    r = np.average(profits)
    std = np.std(profits)
    stdc = np.std(profits[-5:])
    win_count = 0
    for p in profits[::-1]:
        if p <= 0:
            break
        win_count += 1
    std_factor = stdc / std if r > 0 else std / stdc
    metric = abs(r) * std_factor * 0.95 ** win_count * global_factor
    return metric


class BestMetricProcessor(Processor):

    def __init__(self, logging_enabled: bool) -> None:
        super().__init__()
        self._hold_positions = {}
        self._logging_enabled = logging_enabled

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.CLOSE_TO_CLOSE

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return NASDAQ100_SYMBOLS

    def setup(self, hold_positions: List[Position] = ()) -> None:
        for position in hold_positions:
            if position.qty > 0:
                self._hold_positions[position.symbol] = {'side': 'long'}
            else:
                self._hold_positions[position.symbol] = {'side': 'short'}

    def process_all_data(self, contexts: List[Context]) -> List[Action]:
        metrics = []
        volumes = []
        current_prices = {}
        volume_factors = {}
        for context in contexts:
            volume = np.dot(context.interday_lookback['VWAP'], context.interday_lookback['Volume'])
            volumes.append((context.symbol, volume))
        volumes.sort(key=lambda s: s[1], reverse=True)
        for i, symbol in enumerate(volumes):
            volume_factors[symbol[0]] = 1 + 0.1 * i / len(volumes)
        for context in contexts:
            metric = _get_metric(context.interday_lookback, context.current_price, volume_factors[context.symbol])
            metrics.append((context.symbol, metric))
            current_prices[context.symbol] = context.current_price
        metrics.sort(key=lambda s: s[1], reverse=True)
        if self._logging_enabled:
            metric_info = []
            for symbol, metric in metrics[:NUM_HOLD_SYMBOLS + 5]:
                price = current_prices[symbol]
                metric_info.append([symbol, price, metric])
            logging.info('Metric info\n' + tabulate.tabulate(
                metric_info, headers=['Symbol', 'Price', 'Metric'], tablefmt='grid'))
        new_symbols = [s[0] for s in metrics[:NUM_HOLD_SYMBOLS]]
        old_symbols = [symbol for symbol, info in self._hold_positions.items() if info['side'] == 'long']
        actions = []
        for symbol in old_symbols:
            if symbol not in new_symbols and symbol in current_prices:
                actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_prices[symbol]))
                self._hold_positions.pop(symbol)
        for symbol in new_symbols:
            if symbol not in old_symbols:
                actions.append(Action(symbol, ActionType.BUY_TO_OPEN, 1, current_prices[symbol]))
                self._hold_positions[symbol] = {'side': 'long'}
        return actions


class BestMetricProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> BestMetricProcessor:
        return BestMetricProcessor(logging_enabled)
