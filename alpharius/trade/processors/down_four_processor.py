import datetime
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from alpharius.data import DataClient
from ..common import (
    ActionType, Context, Processor, ProcessorFactory, TradingFrequency,
    Position, PositionStatus, ProcessorAction, Mode, DAYS_IN_A_MONTH)
from ..stock_universe import IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 100
N = 4


class DownFourProcessor(Processor):

    def __init__(self,
                 lookback_start_date: pd.Timestamp,
                 lookback_end_date: pd.Timestamp,
                 data_client: DataClient,
                 output_dir: str) -> None:
        super().__init__(output_dir)
        self._positions = dict()
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date,
                                                               lookback_end_date,
                                                               data_client,
                                                               num_stocks=NUM_UNIVERSE_SYMBOLS,
                                                               num_top_volume=1000)
        self._memo = dict()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[pd.Timestamp]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != PositionStatus.ACTIVE]
        for symbol in to_remove:
            self._positions.pop(symbol)
        self._memo.clear()

    def get_stock_universe(self, view_time: pd.Timestamp) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if self.is_active(context.symbol):
            return self._close_position(context)
        elif context.symbol not in self._positions:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t >= datetime.time(15, 0):
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        market_open_price = context.intraday_lookback['Open'].iloc[market_open_index]
        if context.current_price < context.prev_day_close < market_open_price and t <= datetime.time(10, 0):
            return
        intraday_closes = context.intraday_lookback['Close'].tolist()[market_open_index:]
        intraday_opens = context.intraday_lookback['Open'].tolist()[market_open_index:]
        intraday_vols = context.intraday_lookback['Volume'].tolist()[market_open_index:]
        if len(intraday_closes) < N:
            return
        if abs(context.current_price / context.prev_day_close - 1) > 0.5:
            return
        if intraday_closes[-1] > np.min(intraday_closes):
            return
        if intraday_opens[-N] > context.prev_day_close > intraday_closes[-1]:
            return
        if intraday_vols[-2] > intraday_vols[-3]:
            return
        bar_loss = [intraday_closes[i] / intraday_opens[i] - 1 for i in range(-N, 0)]
        for loss in bar_loss:
            if loss >= 0:
                return
            if loss < -0.05:
                return
        h2l = context.h2l_avg
        is_trade = bar_loss[-2] < 0.2 * h2l and bar_loss[-1] > 0.1 * h2l
        o2now = context.current_price / market_open_price - 1
        oc2now = context.current_price / max(market_open_price, context.prev_day_close) - 1
        is_trade = is_trade and o2now < h2l and oc2now > 2 * h2l
        # if is_trade or (context.mode == Mode.TRADE and losses[-2] < 0.25 * h2l):
        #     self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
        #                        f'Prev loss: {losses[-2] * 100:.2f}%. '
        #                        f'Current loss: {losses[-1] * 100:.2f}%. 'aq
        #                        f'H2l: {h2l * 100:.2f}%. Current price {context.current_price}.')
        if is_trade:
            self._positions[context.symbol] = {'entry_time': context.current_time,
                                               'status': PositionStatus.PENDING}
            return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        is_close = context.current_time >= position['entry_time'] + datetime.timedelta(minutes=20)
        self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                           f'Closing position: {is_close}. Current price {context.current_price}.')
        if is_close:
            position['status'] = PositionStatus.CLOSED
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class DownFourProcessorFactory(ProcessorFactory):
    processor_class = DownFourProcessor
