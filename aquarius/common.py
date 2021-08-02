from enum import Enum
from typing import List, Optional, Union
import collections
import datetime
import logging
import os
import pandas as pd
import sys

POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY')
TIME_ZONE = 'America/New_York'
CACHE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'cache')
OUTPUT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'outputs')
DATETIME_TYPE = Union[pd.Timestamp, pd.DatetimeIndex, datetime.datetime]
DAYS_IN_A_WEEK = 5
DAYS_IN_A_MONTH = 20
CALENDAR_DAYS_IN_A_MONTH = 35
DAYS_IN_A_QUARTER = 60
DAYS_IN_A_YEAR = 250
MARKET_OPEN = datetime.time(9, 30)
MARKET_CLOSE = datetime.time(16, 0)
SHORT_RESERVE_RATIO = 1


class TimeInterval(Enum):
    FIVE_MIN = 1
    HOUR = 2
    DAY = 3

    def __str__(self):
        return self.name


class DataSource(Enum):
    POLYGON = 1
    YAHOO = 2

    def __str__(self):
        return self.name


class ActionType(Enum):
    BUY_TO_OPEN = 1
    SELL_TO_OPEN = 2
    BUY_TO_CLOSE = 3
    SELL_TO_CLOSE = 4

    def __str__(self):
        return self.name


Action = collections.namedtuple('Action', ['symbol', 'type', 'percent', 'price'])
Position = collections.namedtuple('Position', ['symbol', 'qty', 'entry_price'])


class DataError(Exception):
    """Error in data loading."""


def timestamp_to_index(index: pd.Index, timestamp: Union[DATETIME_TYPE, datetime.date]) -> int:
    p = None
    for i in range(len(index)):
        if index[i] == timestamp:
            p = i
            break
    return p


def timestamp_to_prev_index(index: pd.Index, timestamp: Union[DATETIME_TYPE, datetime.date]) -> int:
    p = len(index) - 1
    for i in range(len(index)):
        if index[i] > timestamp:
            p = i - 1
            break
    return p


def logging_config(logging_file=None, detail_info=True):
    """Configuration for logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if detail_info:
        formatter = logging.Formatter(
            '[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] [%(threadName)s]\n%(message)s')
    else:
        formatter = logging.Formatter('%(message)s')
    stream_handler = logging.StreamHandler()
    if sys.stdout.isatty():
        stream_handler.setLevel(logging.INFO)
    else:
        stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if logging_file:
        file_handler = logging.FileHandler(logging_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    alpaca_logger = logging.getLogger('alpaca_trade_api')
    alpaca_logger.setLevel(logging.ERROR)


def get_header(title):
    header_left = '== [ %s ] ' % (title,)
    return header_left + '=' * (80 - len(header_left))


class Context:

    def __init__(self,
                 symbol: str,
                 current_time: DATETIME_TYPE,
                 current_price: float,
                 interday_lookback: pd.DataFrame,
                 intraday_lookback: pd.DataFrame) -> None:
        self.symbol = symbol
        self.current_time = current_time
        self.current_price = current_price
        self.interday_lookback = interday_lookback
        self.intraday_lookback = intraday_lookback

    @property
    def prev_day_close(self) -> float:
        return self.interday_lookback.iloc[-1]['Close']


class Processor:

    def __init__(self) -> None:
        pass

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        raise NotImplementedError('Calling parent interface')

    def handle_data(self, context: Context) -> Optional[Action]:
        raise NotImplementedError('Calling parent interface')


class ProcessorFactory:

    def __init__(self) -> None:
        pass

    def create(self, *args, **kwargs) -> Processor:
        raise NotImplementedError('Calling parent interface')
