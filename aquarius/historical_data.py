from .data import *
import functools
import os
import pandas as pd
import polygon

_MEMORY_CACHE_SIZE = 5000
_TIME_ZONE = 'US/Eastern'


class HistoricalData:

    def __init__(self, time_interval: TimeInterval, data_source: DataSource, timeout: float = 5) -> None:
        self._time_interval = time_interval
        self._data_source = data_source
        self._timeout = timeout
        if data_source == DataSource.POLYGON:
            self._init_polygon()

    def _init_polygon(self):
        if POLYGON_API_KEY not in os.environ:
            raise DataError('Polygon API Key not provided')
        self._polygon_client = polygon.RESTClient(auth_key=os.environ[POLYGON_API_KEY], timeout=int(self._timeout))
        if self._time_interval == TimeInterval.FIVE_MIN:
            self._multiplier = 5
            self._timespan = 'minute'
        elif self._time_interval == TimeInterval.HOUR:
            self._multiplier = 1
            self._timespan = 'hour'
        elif self._time_interval == TimeInterval.DAY:
            self._multiplier = 1
            self._timespan = 'day'

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_point(self, ticker, time_point: pd.Timestamp):
        res = self.get_data_list(ticker, time_point, time_point)
        return res[0] if res else None

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_daily_data(self, ticker: str, day: pd.Timestamp):
        day_str = day.strftime('%F')
        start_time = pd.to_datetime(day_str + ' 00:00').tz_localize(tz=_TIME_ZONE)
        end_time = pd.to_datetime(day_str + ' 23:59').tz_localize(tz=_TIME_ZONE)
        return self.get_data_list(ticker, start_time, end_time)

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_list(self, ticker: str, start_time: pd.Timestamp, end_time: pd.Timestamp):
        if self._data_source == DataSource.POLYGON:
            return self._polygon_get_data_list(ticker, start_time, end_time)

    def _cache_get_data_point(self, ticker, time_point):
        pass

    def _polygon_get_data_list(self, ticker: str, start_time: pd.Timestamp, end_time: pd.Timestamp):
        from_ = int(start_time.timestamp() * 1000)
        to = int(end_time.timestamp() * 1000)
        response = self._polygon_client.stocks_equities_aggregates(
            ticker, self._multiplier, self._timespan, from_=from_, to=to, limit=50000)
        if response.status != 'OK':
            raise DataError(f'Polygon response status {response.status}')
        return [DataPoint(o=res['o'], h=res['h'], l=res['l'], c=res['c'], v=res['v'],
                          t=pd.to_datetime(int(res['t']), unit='ms', utc=True).tz_convert(_TIME_ZONE))
                for res in response.results]

