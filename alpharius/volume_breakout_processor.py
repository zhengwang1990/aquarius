from .common import *
from .stock_universe import ThreeSigmaStockUniverse, StockUniverse
from typing import List, Optional
import datetime
import numpy as np

_WATCHING_WINDOW = 6
NUM_UNIVERSE_SYMBOLS = 200


class VolumeBreakoutProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 logging_enabled: bool) -> None:
        super().__init__()
        self._stock_universe = VolumeBreakoutStockUniverse(lookback_start_date=lookback_start_date,
                                                           lookback_end_date=lookback_end_date,
                                                           data_source=data_source)
        self._logging_enabled = logging_enabled
        self._hold_positions = {}

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_universe.get_stock_universe(view_time)

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(15, 0)
                or context.current_time.time() <= datetime.time(10, 0)):
            return
        intraday_lookback = context.intraday_lookback
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        if p is None:
            return
        intraday_closes = intraday_lookback['Close'][p:]
        intraday_volumes = intraday_lookback['Volume'][p:]

        if len(intraday_closes) < _WATCHING_WINDOW:
            return

        vwap = context.vwap
        current_distance = context.current_price - vwap[-1]
        if current_distance > 0 and context.current_price > intraday_closes[-2] > intraday_closes[-3]:
            side = 'long'
            action_type = ActionType.BUY_TO_OPEN
            volume_lookback = 2
        elif current_distance < 0 and context.current_price < intraday_closes[-2] < intraday_closes[-3]:
            side = 'short'
            action_type = ActionType.SELL_TO_OPEN
            volume_lookback = 3
        else:
            return

        # for i in range(2, _WATCHING_WINDOW + 1):
        #     if (intraday_closes[-i] - vwap[-i]) * current_distance > 0:
        #         if self._logging_enabled:
        #             logging.info('Skipping [%s]. Current price [%f]. Distance sign not satisfied.',
        #                          context.symbol, context.current_price)
        #         return

        current_volume = np.min(intraday_volumes[-volume_lookback:])
        volume_threshold = 2 * np.max(intraday_volumes[:-volume_lookback])
        if current_volume < volume_threshold:
            if self._logging_enabled:
                logging.info('Skipping [%s]. Current price [%f]. '
                             'current_volume [%f] < volume_threshold [%f] not satisfied.',
                             context.symbol, context.current_price, current_volume, volume_threshold)
            return

        self._hold_positions[context.symbol] = {'side': side,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price}
        if self._logging_enabled:
            logging.info('Opening [%s]. Current price [%f]. Side [%s].',
                         context.symbol, context.current_price, side)
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        def _pop_position():
            if self._logging_enabled:
                logging.info('Closing [%s]. Current price [%f]. Stop loss [%f].',
                             symbol, current_price, stop_loss)
            self._hold_positions.pop(symbol)
            return action

        symbol = context.symbol
        position = self._hold_positions[symbol]
        entry_time = position['entry_time']
        current_price = context.current_price
        side = position['side']
        stop_loss = context.vwap[-1]
        if side == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            if current_price < stop_loss * 0.98:
                return _pop_position()
        else:
            action = Action(symbol, ActionType.BUY_TO_CLOSE, 1, current_price)
            if current_price > stop_loss * 1.02:
                return _pop_position()
        if (context.current_time - entry_time >= datetime.timedelta(hours=2) or
                context.current_time.time() >= datetime.time(15, 55)):
            return _pop_position()


class VolumeBreakoutProcessorFactory(ProcessorFactory):

    def __init__(self, enable_model=True):
        super().__init__()
        self._enable_model = enable_model

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> VolumeBreakoutProcessor:
        return VolumeBreakoutProcessor(lookback_start_date, lookback_end_date, data_source, logging_enabled)


class VolumeBreakoutStockUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        df = pd.read_csv(os.path.join(DATA_ROOT, 'nasdaq_screener.csv'))
        self._stock_symbols = set(df['Symbol'])

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
            dollar_volumes.append((symbol, dollar_volume))
        dollar_volumes.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in dollar_volumes[:NUM_UNIVERSE_SYMBOLS]]
