from .data import *
import functools
import os
import pandas as pd
import polygon

_MEMORY_CACHE_SIZE = 5000


class HistoricalData:

    def __init__(self, time_interval: TimeInterval, data_source: DataSource, timeout: float = 5) -> None:
        self._time_interval = time_interval
        self._data_source = data_source
        self._timeout = timeout
        if data_source == DataSource.POLYGON:
            if POLYGON_API_KEY not in os.environ:
                raise RuntimeError('Polygon API Key not provided')
            self._polygon_client = polygon.RESTClient(auth_key=os.environ[POLYGON_API_KEY], timeout=int(timeout))

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_point(self, ticker, time_point: pd.Timestamp):
        if self._data_source == DataSource.POLYGON:
            return self._polygon_get_data_point(ticker, time_point)

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_daily_data(self, day):
        pass

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_list(self, start_time, end_time):
        pass

    def _cache_get_data_point(self, ticker, time_point):
        pass

    def _polygon_get_data_point(self, ticker, time_point: pd.Timestamp):
        if self._time_interval == TimeInterval.FIVE_MIN:
            multiplier = 5
            timespan = 'minute'
        elif self._time_interval == TimeInterval.DAY:
            multiplier = 1
            timespan = 'day'
        timestamp = int(time_point.timestamp() * 1000)
        res = self._polygon_client.stocks_equities_aggregates(
            ticker, multiplier, timespan, from_=timestamp, to=timestamp)
        print(res.status)
        return res.results[0]
