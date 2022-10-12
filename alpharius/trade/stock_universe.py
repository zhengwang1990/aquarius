import datetime
import json
import os
from typing import List

import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
from .common import (DataSource, DATETIME_TYPE,
                     DAYS_IN_A_MONTH, CACHE_DIR, timestamp_to_index)
from .constants import COMPANY_SYMBOLS
from .data_loader import load_tradable_history

_STOCK_UNIVERSE_CACHE_ROOT = os.path.join(CACHE_DIR, 'stock_universe')


class StockUniverse:

    def __init__(self,
                 history_start: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        self._historical_data = load_tradable_history(
            history_start, end_time, data_source)

        alpaca = tradeapi.REST()
        calendar = alpaca.get_calendar(start=history_start.strftime('%F'),
                                       end=end_time.strftime('%F'))
        self._market_dates = [pd.to_datetime(
            market_day.date).date() for market_day in calendar]
        self._cache_dir = None

    def get_prev_day(self, view_time: DATETIME_TYPE):
        prev_day = view_time.date() - datetime.timedelta(days=1)
        while prev_day not in self._market_dates:
            prev_day -= datetime.timedelta(days=1)
            if prev_day < self._market_dates[0]:
                raise ValueError(f'{view_time} is too early')
        return pd.to_datetime(prev_day.strftime('%F'))

    def set_cache_dir(self, cache_dir):
        self._cache_dir = os.path.join(_STOCK_UNIVERSE_CACHE_ROOT, cache_dir)
        os.makedirs(self._cache_dir, exist_ok=True)

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        cache_file = None
        if self._cache_dir:
            cache_file = os.path.join(self._cache_dir,
                                      view_time.strftime('%F') + '.json')
            if os.path.isfile(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        stock_universe = self.get_stock_universe_impl(view_time)
        if cache_file:
            with open(cache_file, 'w') as f:
                json.dump(stock_universe, f)
        return stock_universe

    def get_stock_universe_impl(self, view_time: DATETIME_TYPE) -> List[str]:
        raise NotImplementedError('Calling parent interface')


class TopVolumeUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 num_stocks: int = 100):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        self._stock_symbols = set(COMPANY_SYMBOLS)
        self._num_stocks = num_stocks

    def _get_dollar_volume(self, symbol: str, prev_day_ind: int) -> float:
        hist = self._historical_data[symbol]
        pv = [hist['VWAP'][i] * hist['Volume'][i]
              for i in range(max(prev_day_ind - DAYS_IN_A_MONTH + 1, 0), prev_day_ind + 1)]
        return np.average(pv) if pv else 0

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
            dollar_volumes.append((symbol, self._get_dollar_volume(symbol, prev_day_ind)))
        dollar_volumes.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in dollar_volumes[:self._num_stocks]]


class IntradayVolatilityStockUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 num_stocks: int = 50,
                 num_top_volume: int = 500):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        self._stock_symbols = set(COMPANY_SYMBOLS)
        self._top_volumes = TopVolumeUniverse(lookback_start_date,
                                              lookback_end_date,
                                              data_source,
                                              num_top_volume)
        self._num_stocks = num_stocks

    def _get_intraday_range(self, symbol: str, prev_day_ind: int) -> float:
        hist = self._historical_data[symbol]
        res = []
        for i in range(max(prev_day_ind - DAYS_IN_A_MONTH + 1, 1), prev_day_ind + 1):
            h = hist['High'][i]
            l = hist['Low'][i]
            c = hist['Close'][i - 1]
            res.append((h - l) / c)
        return np.average(res) if res else 0

    def get_stock_universe_impl(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        intraday_volatilities = []
        top_volume_symbols = set(
            self._top_volumes.get_stock_universe_impl(view_time))
        for symbol, hist in self._historical_data.items():
            if symbol not in self._stock_symbols:
                continue
            if symbol not in top_volume_symbols:
                continue
            if prev_day not in hist.index:
                continue
            prev_day_ind = timestamp_to_index(hist.index, prev_day)
            if prev_day_ind < DAYS_IN_A_MONTH:
                continue
            intraday_volatility = self._get_intraday_range(
                symbol, prev_day_ind)
            intraday_volatilities.append((symbol, intraday_volatility))

        intraday_volatilities.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in intraday_volatilities[:self._num_stocks]]


class MonthlyGainStockUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 num_stocks: int = 50,
                 num_top_volume: int = 500):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        self._stock_symbols = set(COMPANY_SYMBOLS)
        self._top_volumes = TopVolumeUniverse(lookback_start_date,
                                              lookback_end_date,
                                              data_source,
                                              num_top_volume)
        self._num_stocks = num_stocks

    def _get_monthly_gain(self, symbol: str, prev_day_ind: int) -> float:
        hist = self._historical_data[symbol]
        res = []
        for i in range(max(prev_day_ind - DAYS_IN_A_MONTH + 1, 1), prev_day_ind + 1):
            curr_close = hist['Close'][i]
            prev_close = hist['Close'][i - 1]
            res.append(curr_close / prev_close - 1)
        return np.average(sorted(res)[5:-5]) if res else 0

    def get_stock_universe_impl(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        monthly_returns = []
        top_volume_symbols = set(
            self._top_volumes.get_stock_universe_impl(view_time))
        for symbol, hist in self._historical_data.items():
            if symbol not in self._stock_symbols:
                continue
            if symbol not in top_volume_symbols:
                continue
            if prev_day not in hist.index:
                continue
            prev_day_ind = timestamp_to_index(hist.index, prev_day)
            if prev_day_ind < DAYS_IN_A_MONTH:
                continue
            monthly_return = self._get_monthly_gain(symbol, prev_day_ind)
            monthly_returns.append((symbol, monthly_return))

        monthly_returns.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in monthly_returns[:self._num_stocks]]
