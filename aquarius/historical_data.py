from .common import *
from concurrent import futures
from tqdm import tqdm
from typing import List, Dict
import datetime
import functools
import pandas as pd
import polygon
import sys
import yfinance as yf

_MEMORY_CACHE_SIZE = 5000

_DATA_COLUMNS = ['Open', 'High', 'Low', 'Close', 'Volume', 'VWAP']

_MAX_WORKERS = 5


class HistoricalData:

    def __init__(self, time_interval: TimeInterval, data_source: DataSource, timeout: float = 5) -> None:
        self._time_interval = time_interval
        self._data_source = data_source
        self._timeout = timeout
        if data_source == DataSource.POLYGON:
            self._init_polygon()
        elif data_source == DataSource.YAHOO:
            self._init_yahoo()

    def _init_polygon(self) -> None:
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

    def _init_yahoo(self) -> None:
        if self._time_interval == TimeInterval.FIVE_MIN:
            self._interval = '5m'
        elif self._time_interval == TimeInterval.HOUR:
            self._interval = '1h'
        elif self._time_interval == TimeInterval.DAY:
            self._interval = '1d'

    def get_data_point(self, symbol: str, time_point: DATETIME_TYPE) -> pd.DataFrame:
        return self.get_data_list(symbol, time_point, time_point)

    def get_daily_data(self, symbol: str, day: DATETIME_TYPE) -> pd.DataFrame:
        start_time = pd.Timestamp(year=day.year, month=day.month,
                                  day=day.day, hour=0, minute=0).tz_localize(tz=TIME_ZONE)
        end_time = start_time + datetime.timedelta(days=1)
        return self.get_data_list(symbol, start_time, end_time)

    @functools.lru_cache(maxsize=_MEMORY_CACHE_SIZE)
    def get_data_list(self, symbol: str,
                      start_time: DATETIME_TYPE,
                      end_time: DATETIME_TYPE) -> pd.DataFrame:
        if not start_time.tzinfo:
            start_time = start_time.tz_localize(TIME_ZONE)
        if not end_time.tzinfo:
            end_time = end_time.tz_localize(TIME_ZONE)

        res = None
        if self._data_source == DataSource.POLYGON:
            res = self._polygon_get_data_list(symbol, start_time, end_time)
        if self._data_source == DataSource.YAHOO:
            res = self._yahoo_get_data_list(symbol, start_time, end_time)
        if not res:
            raise DataError(f'{self._data_source} is not supported')

        res.index.rename('Time', inplace=True)
        return res

    def _polygon_get_data_list(self,
                               symbol: str,
                               start_time: DATETIME_TYPE,
                               end_time: DATETIME_TYPE) -> pd.DataFrame:
        from_ = int(start_time.timestamp() * 1000)
        to = int(end_time.timestamp() * 1000 - 1)
        response = self._polygon_client.stocks_equities_aggregates(
            symbol, self._multiplier, self._timespan, from_=from_, to=to, limit=50000)
        if response.status != 'OK':
            raise DataError(f'Polygon response status {response.status}')
        if not hasattr(response, 'results'):
            return pd.DataFrame([], columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        if self._time_interval == TimeInterval.DAY:
            index = [pd.to_datetime(pd.to_datetime(int(res['t']), unit='ms', utc=True).tz_convert(TIME_ZONE).date())
                     for res in response.results]
        else:
            index = [pd.to_datetime(int(res['t']), unit='ms', utc=True).tz_convert(TIME_ZONE)
                     for res in response.results]
        df = pd.DataFrame([[res['o'], res['h'], res['l'], res['c'], res['v'], res['vw']] for res in response.results],
                          index=index,
                          columns=_DATA_COLUMNS)
        return df

    def _yahoo_get_data_list(self,
                             symbol: str,
                             start_time: DATETIME_TYPE,
                             end_time: DATETIME_TYPE) -> pd.DataFrame:
        if self._time_interval != TimeInterval.DAY:
            raise DataError(f'Yahoo data source is not supported for {self._time_interval}')
        t = yf.Ticker(symbol)
        df = t.history(start=start_time, end=end_time, interval=self._interval)
        df['VWAP'] = df.apply(lambda row: (row['High']+row['Low']+row['Close'])/3, axis=1)
        return df[_DATA_COLUMNS]


class HistoricalDataCache:

    def __init__(self, time_interval: TimeInterval, data_source: DataSource, timeout: float = 5) -> None:
        self._data_loader = HistoricalData(time_interval, data_source, timeout)

    def load_history(self,
                     symbols: List[str],
                     start_time: DATETIME_TYPE,
                     end_time: DATETIME_TYPE) -> Dict[str, pd.DataFrame]:
        cache_dir = os.path.join(CACHE_ROOT, start_time.strftime('%F'), end_time.strftime('%F'))
        if symbols:
            os.makedirs(cache_dir, exist_ok=True)
        res = {}
        tasks = {}
        with futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            for symbol in symbols:
                t = pool.submit(self._load_symbol_history, symbol, start_time, end_time)
                tasks[symbol] = t
            iterator = tqdm(tasks.items(), ncols=80) if sys.stdout.isatty() else tasks.items()
            for symbol, t in iterator:
                res[symbol] = t.result()
        return res

    def _load_symbol_history(self,
                             symbol: str,
                             start_time: DATETIME_TYPE,
                             end_time: DATETIME_TYPE) -> pd.DataFrame:
        cache_file = os.path.join(CACHE_ROOT, start_time.strftime('%F'), end_time.strftime('%F'),
                                  f'history_{symbol}.csv')
        if os.path.isfile(cache_file):
            hist = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        else:
            hist = self._data_loader.get_data_list(symbol, start_time, end_time)
            hist.to_csv(cache_file)
        return hist
