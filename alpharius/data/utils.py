import functools
import os
import sys
from concurrent import futures
from typing import Dict, List, Optional, Callable

import pandas as pd
import retrying
from tqdm import tqdm

from .base import DataClient, CACHE_DIR, TimeInterval
from .fmp_client import FmpClient

_MAX_WORKERS = 10
_DEFAULT_DATA_CLIENT = FmpClient()


@retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=500)
def _load_cached_symbol(symbol: str,
                        cache_dir: str,
                        load_func: Callable[[str], pd.DataFrame]) -> pd.DataFrame:
    cache_file = os.path.join(cache_dir, f'history_{symbol}.pickle')
    if os.path.isfile(cache_file):
        hist = pd.read_pickle(cache_file)
    else:
        hist = load_func(symbol)
        hist.to_pickle(cache_file)
    return hist


@functools.lru_cache(maxsize=1)
def load_interday_dataset(symbols: List[str],
                          start_time: pd.Timestamp,
                          end_time: pd.Timestamp,
                          data_client: Optional[DataClient] = _DEFAULT_DATA_CLIENT) -> Dict[str, pd.DataFrame]:
    cache_dir = os.path.join(CACHE_DIR, str(TimeInterval.DAY),
                             start_time.strftime('%F'), end_time.strftime('%F'))
    os.makedirs(cache_dir, exist_ok=True)
    res = {}
    tasks = {}
    load_func = functools.partial(data_client.get_data,
                                  start_time=start_time,
                                  end_time=end_time,
                                  time_interval=TimeInterval.DAY)
    with futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
        for symbol in symbols:
            t = pool.submit(_load_cached_symbol, symbol, cache_dir, load_func)
            tasks[symbol] = t
        iterator = tqdm(tasks.items(), ncols=80) if sys.stdout.isatty() else tasks.items()
        for symbol, t in iterator:
            res[symbol] = t.result()
    return res


def load_intraday_dataset(symbols: List[str],
                          day: pd.Timestamp,
                          data_client: Optional[DataClient] = _DEFAULT_DATA_CLIENT) -> Dict[str, pd.DataFrame]:
    cache_dir = os.path.join(CACHE_DIR, str(TimeInterval.FIVE_MIN), day.strftime('%F'))
    os.makedirs(cache_dir, exist_ok=True)
    res = {}
    tasks = {}
    load_func = functools.partial(data_client.get_daily,
                                  day=day,
                                  time_interval=TimeInterval.FIVE_MIN)
    with futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
        for symbol in symbols:
            t = pool.submit(_load_cached_symbol, symbol, cache_dir, load_func)
            tasks[symbol] = t
        for symbol, t in tasks.items():
            res[symbol] = t.result()
    return res
