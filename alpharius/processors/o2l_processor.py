from alpharius.common import *
from alpharius.data import get_shortable_symbols
from alpharius.stock_universe import IntradayGainStockUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 15
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(13, 0)


class O2lProcessor(Processor):
    """Open to low processor predicts intraday lows based on market open prices."""

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._stock_universe = IntradayGainStockUniverse(lookback_start_date,
                                                         lookback_end_date,
                                                         data_source,
                                                         num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'o2l_processor.txt'),
                                      detail=True,
                                      name='o2l_processor')
        self._shortable_symbols = set(get_shortable_symbols())

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._positions = dict()

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        t = context.current_time.time()
        if t <= ENTRY_TIME or t >= EXIT_TIME:
            return
        interday_opens = context.interday_lookback['Open'][-DAYS_IN_A_MONTH:]
        interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
        o2l_losses = [l / o - 1 for o, l in zip(interday_opens, interday_lows)]
        o2l_avg = np.average(o2l_losses)
        o2l_std = np.std(o2l_losses)
        market_open_ind = 0
        while context.intraday_lookback.index[market_open_ind].time() < datetime.time(9, 30):
            market_open_ind += 1
        market_open_price = context.intraday_lookback['Open'][market_open_ind]
        curent_loss = context.current_price / market_open_price - 1
        threshold = o2l_avg - 4 * o2l_std
        is_trade = curent_loss < threshold
        if is_trade or (context.mode == Mode.TRADE and curent_loss < o2l_avg):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Current loss: {curent_loss * 100:.2f}%. Threshold: {threshold * 100:.2f}%. '
                               f'Current price {context.current_price}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'active'}
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._positions[context.symbol]
        if position['status'] != 'active':
            return
        if (context.current_time >= position['entry_time'] + datetime.timedelta(minutes=15) or
                context.current_time.time() >= EXIT_TIME):
            self._positions['status'] = 'inactive'
            return Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)


class O2lProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> O2lProcessor:
        return O2lProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
