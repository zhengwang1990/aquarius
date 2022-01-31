from .common import *
from .stock_universe import IntradayRangeStockUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 100
NUM_DIRECTIONAL_SYMBOLS = 5
ENTRY_TIME = datetime.time(9, 45)
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
                                                          num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'intraday_reversal_processor.txt'),
                                      detail=True,
                                      name='intraday_reversal_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        [position.symbol for position in self._interday_positions]))

    def setup(self, hold_positions: List[Position]) -> None:
        self._interday_positions = hold_positions

    def process_all_data(self, contexts: List[Context]) -> List[Action]:
        if not contexts:
            return []
        current_time = contexts[0].current_time.time()
        context_dict = {context.symbol: context for context in contexts}
        actions = self._clear_interday_positions(context_dict)
        if current_time == ENTRY_TIME:
            profits = []
            for context in contexts:
                profit = self._get_profit(context)
                if profit is not None:
                    profits.append((context.symbol, profit))
            profits.sort(key=lambda s: s[1])
            n_symbols = len(profits)
            # short_candidates = [s[0] for s in profits[:n_symbols//4]]
            long_candidates = [s[0] for s in profits[-NUM_DIRECTIONAL_SYMBOLS:] if s[1] > 0]
            for symbol in long_candidates:
                context = context_dict[symbol]
                entry_price = context.current_price
                if entry_price > context.prev_day_close:
                    continue
                self._intraday_positions[symbol] = {'side': 'long', 'entry_price': entry_price}
                actions.append(Action(symbol, ActionType.BUY_TO_OPEN, 1, entry_price))
        elif current_time == EXIT_TIME:
            for symbol, info in self._intraday_positions.items():
                action_type = ActionType.SELL_TO_CLOSE if info['side'] == 'long' else ActionType.BUY_TO_CLOSE
                actions.append(Action(symbol, action_type, 1,
                                      context_dict[symbol].current_price
                                      if symbol in context_dict else info['entry_price']))
            self._intraday_positions = dict()
        elif current_time.minute == 0:
            closed_positions = []
            for symbol, info in self._intraday_positions.items():
                if info['side'] == 'long':
                    if symbol in context_dict and context_dict[symbol].current_price / info['entry_price'] < 0.99:
                        actions.append(Action(symbol, ActionType.SELL_TO_CLOSE, 1, context_dict[symbol].current_price))
                        closed_positions.append(symbol)
            for symbol in closed_positions:
                self._intraday_positions.pop(symbol)
        return actions

    @staticmethod
    def _get_profit(context: Context) -> Optional[float]:
        lookback_days = DAYS_IN_A_MONTH
        interday_lookback = context.interday_lookback
        if len(interday_lookback) < lookback_days:
            return None
        closes = interday_lookback['Close'][-lookback_days:]
        opens = interday_lookback['Open'][-lookback_days:]
        values = np.append(closes, context.current_price)
        # profits = [np.log(values[k + 1] / values[k]) for k in range(len(values) - 1)]
        # r = np.average(profits)
        # std = np.std(profits)
        # for t in range(1, 11):
        #     if (profits[-t] - r) / std < -2.5:
        #         return 0
        # if closes[-1] > closes[-5]:
        #     return 0
        intraday_returns = []
        for open_price, close_price in zip(opens, closes):
            intraday_returns.append(np.log(close_price / open_price))
        performance = float(np.sum(intraday_returns))
        return performance

    def _clear_interday_positions(self, context_dict):
        actions = []
        for position in self._interday_positions:
            action_type = ActionType.SELL_TO_CLOSE if position.qty >= 0 else ActionType.BUY_TO_CLOSE
            actions.append(Action(position.symbol, action_type, 1, context_dict[position.symbol].current_price))
        self._interday_positions = []
        return actions


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
