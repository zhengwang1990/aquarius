import datetime
from typing import List, Optional, Tuple

import numpy as np
from ..common import (
    ActionType, Context, DataSource, Processor, ProcessorFactory, TradingFrequency,
    Position, ProcessorAction, Mode, DAYS_IN_A_MONTH, DAYS_IN_A_QUARTER, DATETIME_TYPE)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 40


class H2lFiveMinProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 output_dir: str) -> None:
        super().__init__(output_dir)
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date,
                                                               lookback_end_date,
                                                               data_source,
                                                               num_stocks=NUM_UNIVERSE_SYMBOLS)
        self._memo = dict()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != 'active']
        for symbol in to_remove:
            self._positions.pop(symbol)
        self._memo = dict()

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if self.is_active(context.symbol):
            return self._close_position(context)
        elif context.symbol not in self._positions:
            return self._open_position(context)

    def _get_thresholds(self, context: Context) -> Tuple[float, float]:
        key = context.symbol + context.current_time.strftime('%F')
        if key in self._memo:
            h2l_avg = self._memo[key]
        else:
            interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
            interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
            h2l_losses = [l / h - 1 for h, l in zip(interday_highs, interday_lows)]
            h2l_avg = np.average(h2l_losses)
            self._memo[key] = h2l_avg
        lower_threshold = h2l_avg * 1.5
        upper_threshold = h2l_avg * 0.5
        return lower_threshold, upper_threshold

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if not (datetime.time(10, 0) <= t < datetime.time(10, 30) or
                datetime.time(13, 0) <= t < datetime.time(15, 30)):
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        quarterly_high = np.max(context.interday_lookback['Close'][-DAYS_IN_A_QUARTER:])
        if context.current_price < 0.4 * quarterly_high:
            return
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        if len(intraday_closes) < 2:
            return
        if context.current_price > np.min(intraday_closes):
            return
        if abs(context.current_price / context.prev_day_close - 1) > 0.5:
            return
        intraday_opens = context.intraday_lookback['Open'][market_open_index:]
        if intraday_opens[-2] > context.prev_day_close > intraday_closes[-1]:
            return
        prev_loss = intraday_closes[-2] / intraday_opens[-2] - 1
        current_loss = context.current_price / intraday_closes[-2] - 1
        lower_threshold, upper_threshold = self._get_thresholds(context)
        is_trade = lower_threshold < prev_loss < upper_threshold and prev_loss < current_loss < 0
        if is_trade or (context.mode == Mode.TRADE and prev_loss < upper_threshold * 0.8):
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Prev loss: {prev_loss * 100:.2f}%. '
                               f'Current loss: {current_loss * 100:.2f}%. '
                               f'Threshold: {lower_threshold * 100:.2f}% ~ {upper_threshold * 100:.2f}%. '
                               f'Current price: {context.current_price}. '
                               f'Prev open/close price: {intraday_opens[-2]}/{intraday_closes[-2]}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': 'pending'}
            return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        intraday_closes = context.intraday_lookback['Close']
        take_profit = len(intraday_closes) >= 2 and context.current_price > intraday_closes[-2]
        is_close = (take_profit or
                    context.current_time >= position['entry_time'] + datetime.timedelta(minutes=10))
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Closing position: {is_close}. Current price {context.current_price}.')
        if is_close:
            position['status'] = 'inactive'
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class H2lFiveMinProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> H2lFiveMinProcessor:
        return H2lFiveMinProcessor(lookback_start_date, lookback_end_date, data_source, output_dir)
