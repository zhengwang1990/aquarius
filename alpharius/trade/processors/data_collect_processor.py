import datetime
from typing import List, Optional, Tuple
import os

import numpy as np
import pandas as pd
import sqlite3

from alpharius.data import DataClient
from ..common import (
    ActionType, Context, Processor, ProcessorFactory, TradingFrequency,
    Position, PositionStatus, ProcessorAction, CACHE_DIR)
from ..stock_universe import TopVolumeUniverse, IntradayVolatilityStockUniverse

NUM_UNIVERSE_SYMBOLS = 100
N = 4

INIT_DB = """
CREATE TABLE IF NOT EXISTS data (
    symbol TEXT,
    entry_time TEXT,
    current_bar_loss REAL,
    prev_bar_loss REAL,
    h2l_avg REAL,
    entry_price REAL,
    exit_price_5min REAL,
    exit_price_10min REAL,
    exit_price_15min REAL,
    exit_price_20min REAL,
    UNIQUE (symbol, entry_time)
);
"""


class DataCollectProcessor(Processor):

    def __init__(self,
                 lookback_start_date: pd.Timestamp,
                 lookback_end_date: pd.Timestamp,
                 data_client: DataClient,
                 output_dir: str) -> None:
        super().__init__(output_dir)
        self._positions = dict()
        self._stock_universe = IntradayVolatilityStockUniverse(lookback_start_date, lookback_end_date, data_client, num_top_volume=2000)
        self._skip = False
        self._conn = None

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def setup(self, hold_positions: List[Position], current_time: Optional[pd.Timestamp]) -> None:
        to_remove = [symbol for symbol, position in self._positions.items()
                     if position['status'] != PositionStatus.ACTIVE]
        for symbol in to_remove:
            self._positions.pop(symbol)
        db_dir = os.path.join(CACHE_DIR, 'down_four_data', current_time.strftime('%F'))
        db_file = os.path.join(db_dir, 'data_collect.db')
        self._skip = os.path.isfile(db_file)
        if self._skip:
            return

        os.makedirs(db_dir, exist_ok=True)
        self._conn = sqlite3.connect(db_file)
        self._conn.executescript(INIT_DB)

    def get_stock_universe(self, view_time: pd.Timestamp) -> List[str]:
        return list(set(self._stock_universe.get_stock_universe(view_time) +
                        list(self._positions.keys())))

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if self.is_active(context.symbol):
            return self._close_position(context)
        elif context.symbol not in self._positions:
            return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        if self._skip:
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return

        intraday_closes = context.intraday_lookback['Close'].tolist()[market_open_index:]
        intraday_opens = context.intraday_lookback['Open'].tolist()[market_open_index:]
        intraday_vols = context.intraday_lookback['Volume'].tolist()[market_open_index:]
        h2l_avg = context.h2l_avg

        # Filters
        if len(intraday_closes) < N + 1:
            return
        bar_losses = np.array([intraday_closes[i] / intraday_opens[i] - 1 for i in range(-N, 0)])
        if any(bar_losses > 0):
            return
        if any(bar_losses < -0.05):
            return
        if intraday_vols[-2] > intraday_vols[-3]:
            return

        # Features
        symbol = context.symbol
        current_bar_loss = bar_losses[-1]
        prev_bar_loss = bar_losses[-2]

        self._positions[symbol] = {'entry_time': context.current_time,
                                   'entry_price': context.current_price,
                                   'status': PositionStatus.PENDING,
                                   'current_bar_loss': current_bar_loss,
                                   'prev_bar_loss': prev_bar_loss,
                                   'h2l_avg': h2l_avg}
        return ProcessorAction(symbol, ActionType.BUY_TO_OPEN, 1)

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        position = self._positions[context.symbol]
        timedelta = context.current_time - position['entry_time']

        position[f'exit_price_{timedelta.total_seconds() // 60:.0f}min'] = context.current_price
        is_close = context.current_time >= position['entry_time'] + datetime.timedelta(minutes=20)
        if is_close:
            if 'exit_price_5min' in position and 'exit_price_10min' in position and 'exit_price_15min' in position and 'exit_price_20min' in position:
                self._conn.execute(
                    ('INSERT INTO data '
                     '(symbol, entry_time, current_bar_loss, prev_bar_loss, '
                     'h2l_avg, entry_price, exit_price_5min, exit_price_10min, exit_price_15min, exit_price_20min)'
                     'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (symbol, entry_time) DO NOTHING'),
                    [context.symbol, position['entry_time'].strftime('%F %H:%M:%S'),
                     position['current_bar_loss'], position['prev_bar_loss'],
                     position['h2l_avg'], float(position['entry_price']),
                     float(position['exit_price_5min']), float(position['exit_price_10min']),
                     float(position['exit_price_15min']), float(position['exit_price_20min'])])
                self._conn.commit()
            position['status'] = PositionStatus.CLOSED
            return ProcessorAction(context.symbol, ActionType.SELL_TO_CLOSE, 1)


class DataCollectProcessorFactory(ProcessorFactory):
    processor_class = DataCollectProcessor
