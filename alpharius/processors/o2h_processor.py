from alpharius.common import *
from alpharius.stock_universe import IntradayVolatilityStockUniverse
from alpharius.data import get_shortable_symbols
from typing import List, Optional
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 15
EXIT_TIME = datetime.time(11, 0)


class O2hProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date, lookback_end_date, data_source,
                                                               num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._positions = dict()
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'o2h_processor.txt'),
                                      detail=True,
                                      name='o2h_processor')
        self._shortable_symbols = set(get_shortable_symbols())

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != 'active']
        for symbol in to_remove:
            self._positions.pop(symbol)

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())) & self._shortable_symbols)

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        t = context.current_time.time()
        if t >= EXIT_TIME:
            return
        interday_closes = context.interday_lookback['Close'][-DAYS_IN_A_MONTH:]
        if (context.current_price < 0.8 * interday_closes[-DAYS_IN_A_MONTH] or
                context.current_price > 1.5 * interday_closes[-DAYS_IN_A_MONTH]):
            return
        interday_opens = context.interday_lookback['Open'][-DAYS_IN_A_MONTH:]
        interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
        o2h_gains = [h / o - 1 for o, h in zip(interday_opens, interday_highs)]
        o2h_avg = np.average(o2h_gains)
        o2h_std = np.std(o2h_gains)
        market_open_ind = 0
        while context.intraday_lookback.index[market_open_ind].time() < datetime.time(9, 30):
            market_open_ind += 1
        market_open_price = context.intraday_lookback['Open'][market_open_ind]
        current_gain = context.current_price / market_open_price - 1
        z_score = (current_gain - o2h_avg) / (o2h_std + 1E-7)
        is_trade = 3 > z_score > 2
        if is_trade or (context.mode == Mode.TRADE and current_gain > o2h_avg):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Current gain: {current_gain * 100:.2f}%. Z-score: {z_score}. '
                               f'Current price {context.current_price}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'active'}
            return Action(context.symbol, ActionType.SELL_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._positions[context.symbol]
        if position['status'] != 'active':
            return
        if (context.current_time >= position['entry_time'] + datetime.timedelta(minutes=30) or
                context.current_time.time() >= EXIT_TIME):
            position['status'] = 'inactive'
            return Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)


class O2hProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> O2hProcessor:
        return O2hProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
