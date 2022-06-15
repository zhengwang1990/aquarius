from .common import *
from .constants import COMPANY_SYMBOLS
from .data import load_tradable_history
from typing import List, Optional
import datetime
import numpy as np
import json
import pandas_market_calendars as mcal

_STOCK_UNIVERSE_CACHE_ROOT = os.path.join(CACHE_ROOT, 'stock_universe')


class StockUniverse:

    def __init__(self,
                 history_start: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        self._historical_data = load_tradable_history(history_start, end_time, data_source)

        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=history_start, end_date=end_time)
        self._market_dates = [d.date() for d in mcal.date_range(schedule, frequency='1D')]

        self._price_low, self._price_high = None, None
        self._dvolume_low, self._dvolume_high = None, None
        self._atrp_low, self._atrp_high = None, None
        self._cache_dir = None

    def set_price_filer(self, low: Optional[float] = None, high: Optional[float] = None) -> None:
        self._price_low = low
        self._price_high = high

    def set_dollar_volume_filter(self, low: Optional[float] = None, high: Optional[float] = None) -> None:
        self._dvolume_low = low
        self._dvolume_high = high

    def set_average_true_range_percent_filter(self, low: Optional[float] = None, high: Optional[float] = None) -> None:
        self._atrp_low = low
        self._atrp_high = high

    def _get_dollar_volume(self, symbol: str, prev_day_ind: int) -> float:
        hist = self._historical_data[symbol]
        pv = [hist['VWAP'][i] * hist['Volume'][i]
              for i in range(max(prev_day_ind - DAYS_IN_A_MONTH + 1, 0), prev_day_ind + 1)]
        return np.average(pv) if pv else 0

    def _get_average_true_range_percent(self, symbol: str, prev_day_ind: int) -> float:
        hist = self._historical_data[symbol]
        atrp = []
        for i in range(max(prev_day_ind - DAYS_IN_A_MONTH + 1, 1), prev_day_ind + 1):
            h = hist['High'][i]
            l = hist['Low'][i]
            c = hist['Close'][i - 1]
            atrp.append(max(h - l, h - c, c - l) / c)
        return np.average(atrp) if atrp else 0

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
        res = []
        prev_day = self.get_prev_day(view_time)
        for symbol, hist in self._historical_data.items():
            if prev_day not in hist.index:
                continue
            prev_day_ind = timestamp_to_index(hist.index, prev_day)
            prev_close = hist['Close'][prev_day_ind]
            if self._price_low is not None and prev_close < self._price_low:
                continue
            if self._price_high is not None and prev_close > self._price_high:
                continue
            if self._dvolume_low is not None or self._dvolume_high is not None:
                dvolume = self._get_dollar_volume(symbol, prev_day_ind)
                if self._dvolume_low is not None and dvolume < self._dvolume_low:
                    continue
                if self._dvolume_high is not None and dvolume > self._dvolume_high:
                    continue
            if self._atrp_low is not None or self._atrp_high is not None:
                atrp = self._get_average_true_range_percent(symbol, prev_day_ind)
                if self._atrp_low is not None and atrp < self._atrp_low:
                    continue
                if self._atrp_high is not None and atrp > self._atrp_high:
                    continue
            res.append(symbol)
        return res


class TopVolumeUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 num_stocks: int = 100):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        self._stock_symbols = set(COMPANY_SYMBOLS)
        self._num_stocks = num_stocks

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


class IntradayVolatileStockUniverse(StockUniverse):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 num_stocks: int = 50):
        super().__init__(lookback_start_date, lookback_end_date, data_source)
        self._stock_symbols = set(COMPANY_SYMBOLS)
        self._top_volumes = TopVolumeUniverse(lookback_start_date,
                                              lookback_end_date,
                                              data_source,
                                              1000)
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
        intraday_ranges = []
        top_volume_symbols = set(self._top_volumes.get_stock_universe_impl(view_time))
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
            intraday_range = self._get_intraday_range(symbol, prev_day_ind)
            intraday_ranges.append((symbol, intraday_range))

        intraday_ranges.sort(key=lambda s: s[1], reverse=True)
        return [s[0] for s in intraday_ranges[:self._num_stocks]]
