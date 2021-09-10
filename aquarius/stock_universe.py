from .common import *
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

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
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


class ThreeSigmaStockUniverse(StockUniverse):

    def __init__(self,
                 start_time: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__(start_time, end_time, data_source)
        self.set_dollar_volume_filter(low=1E7)
        self.set_average_true_range_percent_filter(low=0.01)
        self.set_price_filer(low=1)
        self._cache_dir = os.path.join(_STOCK_UNIVERSE_CACHE_ROOT, 'three_sigma')
        os.makedirs(self._cache_dir, exist_ok=True)

    def get_sigma_value(self, symbol: str, prev_day: DATETIME_TYPE) -> float:
        hist = self._historical_data[symbol]
        p = timestamp_to_index(hist.index, prev_day)
        closes = np.array(hist['Close'][max(p - DAYS_IN_A_MONTH + 1, 1):p + 1])
        changes = np.array([np.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)
                            if closes[i + 1] > 0 and closes[i] > 0])
        if not len(changes):
            return 0
        std = np.std(changes)
        mean = np.mean(changes)
        if std < 1E-7:
            return 0
        return np.abs((changes[-1] - mean) / std)

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        cache_file = os.path.join(self._cache_dir,
                                  view_time.strftime('%F') + '.json')
        if os.path.isfile(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        prev_day = self.get_prev_day(view_time)
        symbols = super().get_stock_universe(view_time)
        sigma_values = [(symbol, self.get_sigma_value(symbol, prev_day)) for symbol in symbols]
        sigma_values.sort(key=lambda s: s[1], reverse=True)
        res = [s[0] for s in sigma_values[:50] if s[1] > 3]
        with open(cache_file, 'w') as f:
            json.dump(res, f)
        return res
