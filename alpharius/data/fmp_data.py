import os
from typing import Dict, List, Optional

import pandas as pd
import requests
import retrying

from .base import DATA_COLUMNS, Data, TimeInterval
from alpharius.utils import TIME_ZONE

_FMP_API_KEY_ENV = 'FMP_API_KEY'
_BASE_URL = 'https://financialmodelingprep.com/api/v3/'


class FmpData(Data):

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Instantiates an FMP Data Client.

        Parameters:
            api_key: FMP API key.
        """
        self._api_key = api_key or os.environ[_FMP_API_KEY_ENV]

    @retrying.retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_data(self,
                 symbol: str,
                 start_time: pd.Timestamp,
                 end_time: pd.Timestamp,
                 time_interval: TimeInterval) -> pd.DataFrame:
        """Loads data with specified start and end time."""
        if not start_time.tzinfo:
            start_time = start_time.tz_localize(TIME_ZONE)
        if not end_time.tzinfo:
            end_time = end_time.tz_localize(TIME_ZONE)
        url = _BASE_URL
        if time_interval == TimeInterval.FIVE_MIN:
            url += 'historical-chart/5min/'
        elif time_interval == TimeInterval.HOUR:
            url += 'historical-chart/60min/'
        elif time_interval == TimeInterval.DAY:
            url += 'historical-price-full/'
        else:
            raise ValueError(f'time_interval {time_interval} not supported')
        start = start_time.strftime('%F')
        end = end_time.strftime('%F')
        url += symbol
        params = {'from': start, 'to': end, 'apikey': self._api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        response_json = response.json()
        if isinstance(response_json, dict):
            raw_bars = response_json['historical']
        else:
            raw_bars = response_json
        bars = []
        for bar in raw_bars:
            t = pd.Timestamp(bar['date']).tz_localize(TIME_ZONE)
            if start_time <= t < end_time:
                bars.append(bar)
        bars.sort(key=lambda b: b['date'])
        index = pd.DatetimeIndex([pd.Timestamp(b['date']).tz_localize(TIME_ZONE) for b in bars])
        data = [[b['open'], b['high'], b['low'], b['close'], b['volume']] for b in bars]
        return pd.DataFrame(data, index=index, columns=DATA_COLUMNS)

    def get_last_trades(self, symbols: List[str]) -> Dict[str, float]:
        """Gets the last trade prices of a list of symbols."""
        return {symbol: self._get_last_trade(symbol) for symbol in symbols}

    @retrying.retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def _get_last_trade(self, symbol: str) -> float:
        url = _BASE_URL + 'quote-short/' + symbol
        params = {'apikey': self._api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[0]['price']

