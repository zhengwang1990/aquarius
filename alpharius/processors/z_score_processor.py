from alpharius.common import *
from alpharius.data import get_shortable_symbols
from alpharius.stock_universe import IntradayVolatilityStockUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 40
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(16, 0)


class ZScoreProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date,
                                                               lookback_end_date,
                                                               data_source,
                                                               num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'z_score_processor.txt'),
                                      detail=True,
                                      name='z_score_processor')
        self._shortable_symbols = set(get_shortable_symbols())

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if context.current_time.time() <= ENTRY_TIME or context.current_time.time() >= EXIT_TIME:
            return
        intraday_closes = context.intraday_lookback['Close']
        intraday_volumes = context.intraday_lookback['Volume']
        if len(intraday_closes) < 6:
            return
        price_changes = [abs(intraday_closes[i] - intraday_closes[i - 1])
                         for i in range(1, len(intraday_closes))]
        z_price = (price_changes[-1] - np.mean(price_changes)) / (np.std(price_changes) + 1E-7)
        z_volume = (intraday_volumes[-1] - np.mean(intraday_volumes)) / (np.std(intraday_volumes) + 1E-7)
        is_long = False
        is_short = False
        is_long = is_long or (z_price > 4 and z_volume > 6 and intraday_closes[-1] > intraday_closes[-2])
        is_long = is_long or (z_price > 3 and intraday_closes[-1] < intraday_closes[-2])
        is_short = is_short or (z_price > 3 and z_volume < 0 and intraday_closes[-1] > intraday_closes[-2])
        is_short = is_short and (context.symbol in self._shortable_symbols)
        is_trade = is_long or is_short
        if is_trade or context.mode == Mode.TRADE:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Price z-score: {z_price:.1f}. Volume z-score: {z_volume:.1f}. '
                               f'Current price {context.current_price}.')
        if not is_trade:
            return
        self._positions[context.symbol] = {'entry_time': context.current_time,
                                           'side': 'long' if is_long else 'short'}
        action_type = ActionType.BUY_TO_OPEN if is_long else ActionType.SELL_TO_OPEN
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        position = self._positions[context.symbol]
        if context.current_time < position['entry_time'] + datetime.timedelta(minutes=5):
            return
        action_type = ActionType.SELL_TO_CLOSE if position['side'] == 'long' else ActionType.BUY_TO_CLOSE
        self._positions.pop(context.symbol)
        return Action(context.symbol, action_type, 1, context.current_price)


class ZScoreProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> ZScoreProcessor:
        return ZScoreProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
