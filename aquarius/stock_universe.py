from .common import *
from .exlcusions import EXCLUSIONS
from .data import HistoricalDataCache
from typing import List, Optional
import alpaca_trade_api as tradeapi
import functools
import numpy as np
import pandas_market_calendars as mcal
import re


class StockUniverse:

    def __init__(self, alpaca: Optional[tradeapi.REST] = None) -> None:
        if not alpaca:
            alpaca = tradeapi.REST()
        assets = alpaca.list_assets()
        self._tradable = [asset.symbol for asset in assets
                          if re.match('^[A-Z]*$', asset.symbol)
                          and asset.tradable and asset.marginable
                          and asset.shortable and asset.easy_to_borrow]
        self._tradable = list(set(self._tradable).difference(EXCLUSIONS))
        self._data = None
        self._market_dates = None
        self._price_low, self._price_high = None, None
        self._dvolume_low, self._dvolume_high = None, None
        self._atrp_low, self._atrp_high = None, None

    def set_data_window(self,
                        start_time: DATETIME_TYPE,
                        end_time: DATETIME_TYPE,
                        data_source: DataSource, timeout: float = 5) -> None:
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=start_time, end_date=end_time)
        self._market_dates = [d.date() for d in mcal.date_range(schedule, frequency='1D')]
        cache = HistoricalDataCache(TimeInterval.DAY, data_source, timeout)
        self._data = cache.load_history(self._tradable, start_time, end_time)

    def set_price_filer(self, low: Optional[float] = None, high: Optional[float] = None) -> None:
        self._price_low = low
        self._price_high = high

    def set_dollar_volume_filter(self, low: Optional[float] = None, high: Optional[float] = None) -> None:
        self._dvolume_low = low
        self._dvolume_high = high

    def set_average_true_range_percent_filter(self, low: Optional[float] = None, high: Optional[float] = None) -> None:
        self._atrp_low = low
        self._atrp_high = high

    @functools.lru_cache()
    def _get_dollar_volume(self, symbol: str, prev_day: DATETIME_TYPE) -> float:
        hist = self._data[symbol]
        pv = []
        p = timestamp_to_index(hist.index, prev_day)
        for i in range(max(p - DAYS_IN_A_MONTH + 1, 0), p + 1):
            pv.append(hist.iloc[i]['VWAP'] * hist.iloc[i]['Volume'])
        return np.average(pv) if pv else 0

    @functools.lru_cache()
    def _get_average_true_range_percent(self, symbol: str, prev_day: DATETIME_TYPE) -> float:
        hist = self._data[symbol]
        atrp = []
        p = timestamp_to_index(hist.index, prev_day)
        for i in range(max(p - DAYS_IN_A_MONTH + 1, 1), p + 1):
            h = hist.iloc[i]['High']
            l = hist.iloc[i]['Low']
            c = hist.iloc[i - 1]['Close']
            atrp.append(max(h - l, h - c, c - l) / c)
        return np.average(atrp) if atrp else 0

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        if self._data is None:
            raise ValueError('set_data_window must be called first')

        prev_day = view_time.date() - datetime.timedelta(days=1)
        while prev_day not in self._market_dates:
            prev_day -= datetime.timedelta(days=1)
            if prev_day < self._market_dates[0]:
                raise ValueError(f'{view_time} is too early')
        res = []
        prev_day = pd.to_datetime(prev_day)
        for symbol, hist in self._data.items():
            if prev_day not in hist.index:
                continue
            if self._price_low is not None and hist.loc[prev_day]['Close'] < self._price_low:
                continue
            if self._price_high is not None and hist.loc[prev_day]['Close'] > self._price_high:
                continue
            if self._dvolume_low is not None and self._get_dollar_volume(symbol, prev_day) < self._dvolume_low:
                continue
            if self._dvolume_high is not None and self._get_dollar_volume(symbol, prev_day) > self._dvolume_high:
                continue
            if self._atrp_low is not None and self._get_average_true_range_percent(symbol, prev_day) < self._atrp_low:
                continue
            if self._atrp_high is not None and self._get_average_true_range_percent(symbol, prev_day) > self._atrp_high:
                continue
            res.append(symbol)
        return res
