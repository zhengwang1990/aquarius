from alpharius.common import *
from alpharius.stock_universe import TopVolumeUniverse
from typing import List
import numpy as np
import tabulate

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
        self._universe_symbols = self._stock_universe.get_stock_universe(view_time)
        return list(set(hold_symbols + self._universe_symbols))

    def process_all_data(self, contexts: List[Context]) -> List[Action]:
        current_prices = {context.symbol: context.current_price for context in contexts}
        if not contexts:
            return []
        current_time = contexts[0].current_time
        if current_time.time() < datetime.time(10, 0):
            actions = []
            for position in self._hold_positions:
                action_type = ActionType.SELL_TO_CLOSE if position.qty >= 0 else ActionType.BUY_TO_CLOSE
                actions.append(Action(position.symbol, action_type, 1,
                                      current_prices.get(position.symbol, position.entry_price)))
            return actions

        contexts_selected = [context for context in contexts if context.symbol in self._universe_symbols]
        performances = []
        for context in contexts_selected:
            performances.append((context.symbol, self._get_performance(context)))
        performances.sort(key=lambda s: s[1])
        long_symbols = [s[0] for s in performances[-NUM_DIRECTIONAL_SYMBOLS:] if s[1] > 0]

        self._logging(performances, current_prices, current_time)

        actions = []
        for symbol in long_symbols:
            actions.append(Action(symbol, ActionType.BUY_TO_OPEN, 1, current_prices[symbol]))
        return actions

    def _logging(self, performances, current_prices, current_time):
        performance_info = []
        for symbol, metric in performances[-NUM_DIRECTIONAL_SYMBOLS - 5:]:
            price = current_prices[symbol]
            performance_info.append([symbol, price, metric])
        header = get_header(f'Metric Info {current_time.date()}')
        self._logger.debug(header + '\n' + tabulate.tabulate(
            performance_info, headers=['Symbol', 'Price', 'Performance'], tablefmt='grid'))

    @staticmethod
    def _get_performance(context: Context) -> float:
        interday_lookback = context.interday_lookback
        intraday_lookback = context.intraday_lookback
        if len(interday_lookback) < DAYS_IN_A_YEAR:
            return 0
        closes = interday_lookback['Close'][-DAYS_IN_A_YEAR:]
        ma200 = np.average(closes[-200:])
        if context.current_price < ma200:
            return 0
        values = np.append(closes, context.current_price)
        profits = [np.log(values[k + 1] / values[k]) for k in range(len(values) - 1)]
        r = np.average(profits)
        std = np.std(profits)
        if (profits[-1] - r) / std < -1:
            return 0
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        today_open = intraday_lookback['Open'][p]
        opens = np.append(interday_lookback['Open'][-DAYS_IN_A_YEAR + 1:], today_open)
        overnight_returns = []
        for close_price, open_price in zip(closes, opens):
            overnight_returns.append(np.log(open_price / close_price))
        overnight_returns.sort()
        performance = float(np.sum(overnight_returns[DAYS_IN_A_MONTH:-DAYS_IN_A_MONTH]))
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
