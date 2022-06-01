from alpharius.common import *
from alpharius.stock_universe import TopVolumeUniverse
from typing import List
import datetime
import numpy as np

NUM_UNIVERSE_SYMBOLS = 50
NUM_DIRECTIONAL_SYMBOLS = 5
ENTRY_TIME = datetime.time(10, 0)
EXIT_TIME = datetime.time(15, 30)


class IntradayMomentumProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__()
        self._positions = dict()
        self._stock_universe = TopVolumeUniverse(lookback_start_date,
                                                 lookback_end_date,
                                                 data_source,
                                                 num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'intraday_momentum_processor.txt'),
                                      detail=True,
                                      name='intraday_momentum_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._positions = {
            position.symbol: {'side': 'long' if position.qty > 0 else 'short'}
            for position in hold_positions
        }

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _open_position(self, context: Context):
        if context.current_time.time() != datetime.time(12, 0):
            return

        interday_closes = context.interday_lookback['Close']
        intraday_closes = context.intraday_lookback['Close']
        if len(interday_closes) < DAYS_IN_A_YEAR:
            return
        market_open = pd.to_datetime(
            pd.Timestamp.combine(context.current_time.date(), MARKET_OPEN)).tz_localize(TIME_ZONE)
        open_index = timestamp_to_index(intraday_closes.index, market_open)
        if open_index is None:
            return
        prev_day_close = context.prev_day_close
        abs_profits = [abs(interday_closes[i] / interday_closes[i - 1] - 1) for i in range(1, len(interday_closes))]
        daily_volatility = abs(context.current_price / prev_day_close - 1)
        weekly_volatility = np.average(abs_profits[-DAYS_IN_A_WEEK:])
        monthly_volatility = np.average(abs_profits[-DAYS_IN_A_MONTH:])
        yearly_volatility = np.average(abs_profits[-DAYS_IN_A_YEAR:])
        if weekly_volatility < 1.5 * monthly_volatility:
            return
        if daily_volatility > monthly_volatility:
            return

        open_price = intraday_closes[open_index]
        action = None
        if context.current_price < open_price < prev_day_close:
            self._positions[context.symbol] = {'side': 'short'}
            action = Action(context.symbol, ActionType.SELL_TO_OPEN, 1, context.current_price)
        elif context.current_price > open_price > prev_day_close:
            self._positions[context.symbol] = {'side': 'long'}
            action = Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

        if action is not None:
            self._logger.debug('[%s] [%s] Current price %.2f, Open Price %.2f, Prev Close %.2f.'
                               'Daily volatility %.2f, monthly volatility %.2f, Yearly volatility %.2f',
                               context.current_time.date(), context.symbol,
                               context.current_price, open_price, prev_day_close,
                               daily_volatility, monthly_volatility, yearly_volatility)

        return action

    def _close_position(self, context: Context):
        if context.current_time.time() != datetime.time(16, 0):
            return
        symbol = context.symbol
        side = self._positions[symbol]['side']
        if side == 'long':
            action = Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)
        else:
            action = Action(context.symbol, ActionType.BUY_TO_CLOSE, 1, context.current_price)
        self._positions.pop(symbol)
        return action


class IntradayMomentumProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> IntradayMomentumProcessor:
        return IntradayMomentumProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
