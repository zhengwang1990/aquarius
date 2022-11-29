import os
import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import tabulate
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, DATETIME_TYPE, DAYS_IN_A_YEAR, DAYS_IN_A_QUARTER,
    DAYS_IN_A_WEEK, logging_config, get_header)
from ..stock_universe import TopVolumeUniverse

NUM_UNIVERSE_SYMBOLS = 200
NUM_DIRECTIONAL_SYMBOLS = 5


class OvernightProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._stock_universe = TopVolumeUniverse(lookback_start_date, lookback_end_date, data_source,
                                                 num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._universe_symbols = []
        self._hold_positions = []
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'overnight_processor.txt'),
                                      detail=True,
                                      name='overnight_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.CLOSE_TO_OPEN

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._hold_positions = hold_positions

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        hold_symbols = [position.symbol for position in self._hold_positions]
        self._universe_symbols = self._stock_universe.get_stock_universe(
            view_time)
        return list(set(hold_symbols + self._universe_symbols))

    def process_all_data(self, contexts: List[Context]) -> List[ProcessorAction]:
        current_prices = {
            context.symbol: context.current_price for context in contexts}
        if not contexts:
            return []
        current_time = contexts[0].current_time
        if current_time.time() < datetime.time(10, 0):
            actions = []
            for position in self._hold_positions:
                if position.symbol not in current_prices:
                    self._logger.warning('Position [%s] not found in contexts', position.symbol)
                    continue
                action_type = ActionType.SELL_TO_CLOSE if position.qty >= 0 else ActionType.BUY_TO_CLOSE
                actions.append(ProcessorAction(position.symbol, action_type, 1))
            return actions

        contexts_selected = [
            context for context in contexts if context.symbol in self._universe_symbols]
        performances = []
        for context in contexts_selected:
            performances.append((context.symbol, self._get_performance(context)))
        performances.sort(key=lambda s: s[1], reverse=True)
        long_symbols = [s[0]
                        for s in performances[:NUM_DIRECTIONAL_SYMBOLS] if s[1] > 0]

        self._logging(performances, current_prices, current_time)

        actions = []
        for symbol in long_symbols:
            actions.append(ProcessorAction(symbol, ActionType.BUY_TO_OPEN, 1))
        return actions

    def _logging(self,
                 performances: List[Tuple[str, float]],
                 current_prices: Dict[str, float],
                 current_time: DATETIME_TYPE) -> None:
        performance_info = []
        for symbol, metric in performances[:NUM_DIRECTIONAL_SYMBOLS + 15]:
            price = current_prices[symbol]
            performance_info.append([symbol, price, metric])
        header = get_header(f'Metric Info {current_time.date()}')
        self._logger.debug('\n' + header + '\n' + tabulate.tabulate(
            performance_info, headers=['Symbol', 'Price', 'Performance'], tablefmt='grid'))

    @staticmethod
    def _get_performance(context: Context) -> float:
        interday_lookback = context.interday_lookback
        if len(interday_lookback) < DAYS_IN_A_YEAR:
            return 0
        closes = interday_lookback['Close'][-DAYS_IN_A_YEAR:]
        values = np.append(closes, context.current_price)
        profits = [np.log(values[k + 1] / values[k])
                   for k in range(len(values) - 1)]
        r = np.average(profits)
        std = np.std(profits)
        if (profits[-1] - r) / std < -1:
            return 0
        today_open = context.today_open
        opens = np.append(
            interday_lookback['Open'][-DAYS_IN_A_YEAR + 1:], today_open)
        overnight_returns = []
        for close_price, open_price in zip(closes, opens):
            overnight_returns.append(np.log(open_price / close_price))
        quarterly = np.sum(overnight_returns[-DAYS_IN_A_QUARTER:])
        weekly = np.sum(overnight_returns[-DAYS_IN_A_WEEK:])
        if quarterly < 0 and weekly < 0:
            return 0
        yearly = np.sum(sorted(overnight_returns)[30:-30])
        performance = yearly + 0.3 * quarterly + 0.3 * weekly
        return performance


class OvernightProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> OvernightProcessor:
        return OvernightProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
