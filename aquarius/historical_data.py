from .common import *
from typing import Union
from dateutil.relativedelta import relativedelta
import datetime
import functools
import os
import pandas as pd
import polygon

_MEMORY_CACHE_SIZE = 5000

_DATETIME_TYPE = Union[pd.Timestamp, pd.DatetimeIndex, datetime.datetime]

_DATA_COLUMNS = ['Open', 'High', 'Low', 'Close', 'Volume']


def _get_day_start(time_point: _DATETIME_TYPE) -> _DATETIME_TYPE:
    return pd.Timestamp(year=time_point.year, month=time_point.month,
                        day=time_point.day, hour=0, minute=0).tz_localize(tz=TIME_ZONE)


def _get_day_end(time_point: _DATETIME_TYPE) -> _DATETIME_TYPE:
    return pd.Timestamp(year=time_point.year, month=time_point.month,
                        day=time_point.day, hour=23, minute=59).tz_localize(tz=TIME_ZONE)


def _get_month_start(time_point: _DATETIME_TYPE) -> _DATETIME_TYPE:
    return pd.Timestamp(year=time_point.year, month=time_point.month,
                        day=1, hour=0, minute=0).tz_localize(tz=TIME_ZONE)


def _get_month_end(time_point: _DATETIME_TYPE) -> datetime.datetime:
    return _get_month_start(time_point) + relativedelta(months=1) - relativedelta(seconds=1)


class HistoricalData:

    def __init__(self, time_interval: TimeInterval, data_source: DataSource, timeout: float = 5) -> None:
        self._time_interval = time_interval
        self._data_source = data_source
        self._timeout = timeout
        if data_source == DataSource.POLYGON:
            self._init_polygon()

    def _init_polygon(self):
        if not POLYGON_API_KEY:
            raise DataError('Polygon API Key not provided')
        self._polygon_client = polygon.RESTClient(auth_key=POLYGON_API_KEY, timeout=int(self._timeout))
        if self._time_interval == TimeInterval.FIVE_MIN:
            self._multiplier = 5
            self._timespan = 'minute'
        elif self._time_interval == TimeInterval.HOUR:
            self._multiplier = 1
            self._timespan = 'hour'
        elif self._time_interval == TimeInterval.DAY:
            self._multiplier = 1
            self._timespan = 'day'

    def get_data_point(self, ticker, time_point: _DATETIME_TYPE) -> pd.DataFrame:
        return self.get_data_list(ticker, time_point, time_point)

    def get_daily_data(self, ticker: str, day: _DATETIME_TYPE) -> pd.DataFrame:
        start_time = _get_day_start(day)
        end_time = _get_day_end(day)
        return self.get_data_list(ticker, start_time, end_time)

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_list(self, ticker: str,
                      start_time: _DATETIME_TYPE,
                      end_time: _DATETIME_TYPE) -> pd.DataFrame:
        if not start_time.tzinfo:
            start_time = start_time.tz_localize(TIME_ZONE)
        if not end_time.tzinfo:
            end_time = end_time.tz_localize(TIME_ZONE)
        if self._time_interval == TimeInterval.FIVE_MIN or self._time_interval == TimeInterval.HOUR:
            return self._get_intraday_data_list(ticker, start_time, end_time)

        return self._get_interday_data_list(ticker, start_time, end_time)

    def _get_interday_data_list(self,
                                ticker: str,
                                start_time: _DATETIME_TYPE,
                                end_time: _DATETIME_TYPE) -> pd.DataFrame:
        if ((start_time.day != 1 or (end_time + relativedelta(days=1)).day != 1)
                and start_time.month == end_time.month):
            return self._datasource_get_data_list(ticker, start_time, end_time)

        first_month = _get_month_start(start_time)
        if start_time.day != 1:
            first_month += relativedelta(months=1)
        last_month = _get_month_end(end_time)
        if (end_time + relativedelta(days=1)).day != 1:
            last_month -= relativedelta(months=1)

        curr_month = first_month
        res = pd.DataFrame([], columns=_DATA_COLUMNS)
        while curr_month <= last_month:
            cache_file = os.path.join(CACHE_ROOT, str(self._time_interval),
                                      curr_month.strftime('%Y-%m'), ticker + '.csv')
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            else:
                month_start_time = _get_month_start(curr_month)
                month_end_time = _get_month_end(curr_month)
                df = self._datasource_get_data_list(ticker, month_start_time, month_end_time)
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                df.to_csv(cache_file)
            res = pd.concat([res, df])
            curr_month += relativedelta(months=1)

        if start_time.day != 1:
            month_end_time = _get_month_end(start_time)
            df = self._datasource_get_data_list(ticker, start_time, month_end_time)
            res = pd.concat([df, res])
        if (end_time + relativedelta(days=1)).day != 1:
            month_start_time = _get_month_start(end_time)
            df = self._datasource_get_data_list(ticker, month_start_time, end_time)
            res = pd.concat([res, df])

        res.index.rename('Time', inplace=True)
        return res

    def _get_intraday_data_list(self,
                                ticker: str,
                                start_time: _DATETIME_TYPE,
                                end_time: _DATETIME_TYPE) -> pd.DataFrame:
        if ((start_time.time() > datetime.time(4) or end_time.time() < datetime.time(20))
                and start_time.date() == end_time.date()):
            return self._datasource_get_data_list(ticker, start_time, end_time)

        first_day = _get_day_start(start_time)
        if start_time.time() > datetime.time(4):
            first_day += datetime.timedelta(days=1)
        last_day = end_time
        if end_time.time() < datetime.time(20):
            last_day -= datetime.timedelta(days=1)

        curr_day = first_day
        res = pd.DataFrame([], columns=_DATA_COLUMNS)
        while curr_day <= last_day:
            if curr_day.isoweekday() >= 6:
                curr_day += datetime.timedelta(days=1)
                continue
            cache_file = os.path.join(CACHE_ROOT, str(self._time_interval), curr_day.strftime('%F'), ticker + '.csv')
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            else:
                day_start_time = _get_day_start(curr_day)
                day_end_time = _get_day_end(curr_day)
                df = self._datasource_get_data_list(ticker, day_start_time, day_end_time)
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                df.to_csv(cache_file)
            res = pd.concat([res, df])
            curr_day += datetime.timedelta(days=1)

        if start_time.time() > datetime.time(4):
            day_end_time = _get_day_end(start_time)
            df = self._datasource_get_data_list(ticker, start_time, day_end_time)
            print(start_time, day_end_time)
            res = pd.concat([df, res])
        if end_time.time() < datetime.time(20):
            day_start_time = _get_day_start(end_time)
            df = self._datasource_get_data_list(ticker, day_start_time, end_time)
            res = pd.concat([res, df])

        res.index.rename('Time', inplace=True)
        return res

    def _datasource_get_data_list(self,
                                  ticker: str,
                                  start_time: _DATETIME_TYPE,
                                  end_time: _DATETIME_TYPE) -> pd.DataFrame:
        if self._data_source == DataSource.POLYGON:
            return self._polygon_get_data_list(ticker, start_time, end_time)

    def _polygon_get_data_list(self,
                               ticker: str,
                               start_time: _DATETIME_TYPE,
                               end_time: _DATETIME_TYPE) -> pd.DataFrame:
        from_ = int(start_time.timestamp() * 1000)
        to = int(end_time.timestamp() * 1000)
        response = self._polygon_client.stocks_equities_aggregates(
            ticker, self._multiplier, self._timespan, from_=from_, to=to, limit=50000)
        if response.status != 'OK':
            raise DataError(f'Polygon response status {response.status}')
        if not hasattr(response, 'results'):
            return pd.DataFrame([], columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        df = pd.DataFrame([[res['o'], res['h'], res['l'], res['c'], res['v']] for res in response.results],
                          index=[pd.to_datetime(int(res['t']), unit='ms', utc=True).tz_convert(TIME_ZONE)
                                 for res in response.results],
                          columns=_DATA_COLUMNS)
        return df
