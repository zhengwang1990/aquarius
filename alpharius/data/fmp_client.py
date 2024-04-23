import collections
import contextlib
import os
import time
from typing import Dict, List, Optional

import pandas as pd
import requests
import retrying

from alpharius.utils import TIME_ZONE
from .base import DATA_COLUMNS, DataClient, TimeInterval

_FMP_API_KEY_ENV = 'FMP_API_KEY'
_BASE_URL = 'https://financialmodelingprep.com/api/v3/'


class FmpClient(DataClient):

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Instantiates an FMP Data Client.

        Parameters:
            api_key: FMP API key.
        """
        self._api_key = api_key or os.environ[_FMP_API_KEY_ENV]
        self._call_history = collections.deque()
        self._max_calls = 300
        self._period = 60

    @contextlib.contextmanager
    def rate_limit(self):
        def remove_queue():
            while self._call_history and self._call_history[0] < time.time() - self._period:
                self._call_history.popleft()

        remove_queue()
        while len(self._call_history) >= self._max_calls:
            wait_time = max(self._call_history[0] + 60 - time.time(), 0)
            time.sleep(wait_time)
            remove_queue()
        yield
        self._call_history.append(time.time())

    @retrying.retry(stop_max_attempt_number=3, wait_exponential_multiplier=500)
    def get_data(self,
                 symbol: str,
                 start_time: pd.Timestamp,
                 end_time: pd.Timestamp,
                 time_interval: TimeInterval) -> pd.DataFrame:
        """Loads data with specified start and end time.

        start_time and end_time are inclusive.
        """
        if not start_time.tzinfo:
            start_time = start_time.tz_localize(TIME_ZONE)
        if not end_time.tzinfo:
            end_time = end_time.tz_localize(TIME_ZONE)
        url = _BASE_URL
        if time_interval == TimeInterval.FIVE_MIN:
            url += 'historical-chart/5min/'
        elif time_interval == TimeInterval.HOUR:
            url += 'historical-chart/1hour/'
        elif time_interval == TimeInterval.DAY:
            url += 'historical-price-full/'
        else:
            raise ValueError(f'time_interval {time_interval} not supported')
        start = start_time.strftime('%F')
        end = end_time.strftime('%F')
        url += symbol
        params = {'from': start, 'to': end, 'apikey': self._api_key}
        with self.rate_limit():
            response = requests.get(url, params=params)
            response.raise_for_status()
        response_json = response.json()
        if isinstance(response_json, dict):
            raw_bars = response_json.get('historical', [])
        else:
            raw_bars = response_json
        bars = []
        for bar in raw_bars:
            t = pd.Timestamp(bar['date']).tz_localize(TIME_ZONE)
            if time_interval == time_interval.DAY or start_time <= t <= end_time:
                bars.append(bar)
        bars.sort(key=lambda b: b['date'])
        index = pd.DatetimeIndex([pd.Timestamp(b['date']).tz_localize(TIME_ZONE) for b in bars])
        data = [[b['open'], b['high'], b['low'], b['close'], b['volume']] for b in bars]
        return pd.DataFrame(data, index=index, columns=DATA_COLUMNS)

    def get_last_trades(self, symbols: List[str]) -> Dict[str, float]:
        """Gets the last trade prices of a list of symbols."""
        return {symbol: self._get_last_trade(symbol) for symbol in symbols}

    @retrying.retry(stop_max_attempt_number=3, wait_exponential_multiplier=500)
    def _get_last_trade(self, symbol: str) -> float:
        url = _BASE_URL + 'quote-short/' + symbol
        params = {'apikey': self._api_key}
        with self.rate_limit():
            response = requests.get(url, params=params)
            response.raise_for_status()
        return response.json()[0]['price']
