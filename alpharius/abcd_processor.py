from .common import *
from .stock_universe import StockUniverse
from typing import List, Optional
import datetime
import numpy as np
import os
import pandas as pd
import sqlite3

_WATCHING_WINDOW = 18
_INTRA_DAY_RANGE_PORTION = 0.2
_HISTORY_DATA_COLUMNS = ['Date', 'Symbol', 'Gain']


class AbcdProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 logging_enabled: bool,
                 _history_db_path: Optional[str] = None) -> None:
        super().__init__()
        self._stock_universe = StockUniverse(history_start=lookback_start_date,
                                             end_time=lookback_end_date,
                                             data_source=data_source)
        self._stock_universe.set_dollar_volume_filter(low=1E7)
        self._stock_universe.set_price_filer(low=5)
        self._stock_universe.set_average_true_range_percent_filter(low=0.01)
        self._logging_enabled = logging_enabled
        self._hold_positions = {}
        self._history_db_path = _history_db_path
        self._history_data = []

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        if not self._history_db_path:
            return self._stock_universe.get_stock_universe(view_time)
        conn = sqlite3.connect(self._history_db_path)
        start_time = (view_time - datetime.timedelta(days=60)).date()
        end_time = view_time.date()
        query = ('SELECT Symbol, AVG(Gain) AS Gain FROM AbcdHistory '
                 f'WHERE Date > "{start_time}" AND Date < "{end_time}" '
                 'GROUP BY Symbol')
        df = pd.read_sql_query(query, conn)
        qualified = [(row.Symbol, row.Gain) for row in df.itertuples() if row.Gain > 0]
        qualified.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in qualified[:10]]

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(15, 55)
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

        if len(intraday_lookback) < _WATCHING_WINDOW + p:
            return

        intraday_closes = np.array(intraday_lookback['Close'])
        intraday_opens = np.array(intraday_lookback['Open'])
        intraday_highs = np.array(intraday_lookback['High'])
        intraday_lows = np.array(intraday_lookback['Low'])
        intraday_range = np.max(intraday_highs) - np.min(intraday_lows)
        if intraday_range / context.prev_day_close < 0.01:
            return

        if intraday_closes[-1] < intraday_opens[-1]:
            return

        current_index = len(intraday_lookback) - 1
        flat_value = intraday_closes[current_index]
        flat_start = current_index - 1
        for i in range(flat_start - 1, -1, -1):
            if intraday_closes[i] < flat_value:
                flat_value = intraday_closes[i]
            if intraday_closes[i] > flat_value + _INTRA_DAY_RANGE_PORTION * intraday_range:
                flat_start = i + 1
                break

        peak_start = flat_start - 1
        peak_value = intraday_closes[flat_start]
        for i in range(peak_start - 1, -1, -1):
            if intraday_closes[i] > peak_value:
                peak_value = intraday_closes[i]
            if intraday_closes[i] < peak_value - _INTRA_DAY_RANGE_PORTION * intraday_range:
                peak_start = i + 1
                break

        trough_value = intraday_closes[peak_start]
        trough_start = peak_start - 1
        for i in range(trough_start - 1, -1, -1):
            if intraday_closes[i] < trough_value:
                trough_value = intraday_closes[i]
            if intraday_closes[i] > trough_value + _INTRA_DAY_RANGE_PORTION * intraday_range:
                trough_start = i + 1
                break

        if flat_value < trough_value:
            return

        support_value = intraday_closes[trough_start]
        support_start = trough_start - 1
        for i in range(support_start - 1, -1, -1):
            if intraday_closes[i] > support_value:
                support_value = intraday_closes[i]
            if intraday_closes[i] < support_value - _INTRA_DAY_RANGE_PORTION * intraday_range:
                support_start = i + 1
                break

        if support_start <= p:
            return

        if not peak_value > support_value > trough_value:
            return

        if abs(context.current_price - support_value) > _INTRA_DAY_RANGE_PORTION * 0.3 * intraday_range:
            return

        # print(context.current_time.time(), intraday_range)
        # print('Current', current_index, intraday_lookback.index[current_index], context.current_price)
        # print('Flat', flat_start, intraday_lookback.index[flat_start], flat_value)
        # print('Peak', peak_start, intraday_lookback.index[peak_start], peak_value)
        # print('Trough', trough_start, intraday_lookback.index[trough_start], trough_value)
        # print('Support', support_start, intraday_lookback.index[support_start], support_value)

        side = 'long'
        action_type = ActionType.BUY_TO_OPEN

        take_profit = peak_value

        self._hold_positions[context.symbol] = {'side': side,
                                                'take_profit': take_profit,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        def _pop_position():
            self._hold_positions.pop(symbol)
            if side == 'long':
                gain = current_price / entry_price - 1 - BID_ASK_SPREAD
            else:
                gain = 1 - current_price / entry_price - BID_ASK_SPREAD
            self._history_data.append([context.current_time.date(), symbol, gain])
            return action

        symbol = context.symbol
        position = self._hold_positions[symbol]
        entry_time = position['entry_time']
        entry_price = position['entry_price']
        current_price = context.current_price
        side = position['side']

        if side == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
        else:
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            return _pop_position()

    def teardown(self, output_dir: str) -> None:
        if self._history_db_path:
            return
        history_db_path = os.path.join(output_dir, 'history.db')
        conn = sqlite3.connect(history_db_path)
        df = pd.DataFrame(self._history_data, columns=_HISTORY_DATA_COLUMNS)
        df.to_sql('AbcdHistory', conn, if_exists='append')
        conn.close()


class AbcdProcessorFactory(ProcessorFactory):

    def __init__(self, history_db_path=None):
        super().__init__()
        self._history_db_path = history_db_path

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               logging_enabled: bool = False,
               *args, **kwargs) -> AbcdProcessor:
        return AbcdProcessor(lookback_start_date, lookback_end_date, data_source, logging_enabled,
                             self._history_db_path)
