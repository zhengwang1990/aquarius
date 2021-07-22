from .common import *
from typing import Union
import datetime
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

    def get_data_point(self, ticker, time_point: Union[pd.Timestamp, pd.DatetimeIndex]):
        res = self.get_data_list(ticker, time_point, time_point)
        return res[0] if res else None

    def get_daily_data(self, ticker: str, day: Union[pd.Timestamp, pd.DatetimeIndex]):
        day_str = day.strftime('%F')
        start_time = pd.to_datetime(day_str + ' 00:00').tz_localize(tz=TIME_ZONE)
        end_time = pd.to_datetime(day_str + ' 23:59').tz_localize(tz=TIME_ZONE)
        return self.get_data_list(ticker, start_time, end_time)

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_list(self, ticker: str,
                      start_time: Union[pd.Timestamp, pd.DatetimeIndex],
                      end_time: Union[pd.Timestamp, pd.DatetimeIndex]):
        # A strict subset of a day
        if (start_time.time() > datetime.time(4) or end_time.time() < datetime.time(21)
                and start_time.date() == end_time.date()):
            return self._datasource_get_data_list(ticker, start_time, end_time)

        first_day = start_time.date()
        if start_time.time() > datetime.time(4):
            first_day += datetime.timedelta(days=1)
        last_day = end_time.date()
        if end_time.time() < datetime.time(21):
            last_day -= datetime.timedelta(days=1)

        curr_day = first_day
        res = pd.DataFrame([], columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        while curr_day <= last_day:
            cache_file = os.path.join(CACHE_ROOT, str(self._time_interval), curr_day.strftime('%F'), ticker + '.csv')
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            else:
                day_str = curr_day.strftime('%F')
                day_start_time = pd.to_datetime(day_str + ' 00:00').tz_localize(tz=TIME_ZONE)
                day_end_time = pd.to_datetime(day_str + ' 23:59').tz_localize(tz=TIME_ZONE)
                df = self._datasource_get_data_list(ticker, day_start_time, day_end_time)
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                df.to_csv(cache_file)
            res = pd.concat([res, df])
            curr_day += datetime.timedelta(days=1)

        if start_time.time() > datetime.time(4):
            day_end_time = pd.to_datetime(start_time.strftime('%F') + ' 23:59').tz_localize(tz=TIME_ZONE)
            df = self._datasource_get_data_list(ticker, start_time, day_end_time)
            res = pd.concat([df, res])

        if end_time.time() < datetime.time(21):
            day_start_time = pd.to_datetime(end_time.strftime('%F') + ' 00:00').tz_localize(tz=TIME_ZONE)
            df = self._datasource_get_data_list(ticker, day_start_time, end_time)
            res = pd.concat([res, df])
        return res

    def _datasource_get_data_list(self,
                                  ticker: str,
                                  start_time: Union[pd.Timestamp, pd.DatetimeIndex],
                                  end_time: Union[pd.Timestamp, pd.DatetimeIndex]):
        if self._data_source == DataSource.POLYGON:
            return self._polygon_get_data_list(ticker, start_time, end_time)

    def _polygon_get_data_list(self,
                               ticker: str,
                               start_time: Union[pd.Timestamp, pd.DatetimeIndex],
                               end_time: Union[pd.Timestamp, pd.DatetimeIndex]):
        from_ = int(start_time.timestamp() * 1000)
        to = int(end_time.timestamp() * 1000)
        response = self._polygon_client.stocks_equities_aggregates(
            ticker, self._multiplier, self._timespan, from_=from_, to=to, limit=50000)
        if response.status != 'OK':
            raise DataError(f'Polygon response status {response.status}')
        df = pd.DataFrame([[res['o'], res['h'], res['l'], res['c'], res['v']] for res in response.results],
                          index=pd.Index([pd.to_datetime(int(res['t']), unit='ms', utc=True).tz_convert(TIME_ZONE)
                                          for res in response.results],
                                         name='Time'),
                          columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        return df
