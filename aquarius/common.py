from enum import Enum
from typing import List, Union
import collections
import datetime
import os
import pandas as pd

POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY')
TIME_ZONE = 'America/New_York'
CACHE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'cache')
DATETIME_TYPE = Union[pd.Timestamp, pd.DatetimeIndex, datetime.datetime]
DAYS_IN_A_WEEK = 5
DAYS_IN_A_MONTH = 20
DAYS_IN_A_QUARTER = 60
DAYS_IN_A_YEAR = 250


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


Action = collections.namedtuple('Action', ['symbol', 'type', 'size', 'weight'], defaults=[None])


class DataError(Exception):
    """Error in data loading."""


def timestamp_to_index(index: pd.Index, timestamp: DATETIME_TYPE) -> int:
    p = None
    for i in range(len(index)):
        if index[i] == timestamp:
            p = i
            break
    return p


class Processor:

    def __init__(self):
        pass

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        raise NotImplementedError('Calling parent interface')

    def handle_data(self, context, data) -> Action:
        raise NotImplementedError('Calling parent interface')


class Context:

    def __init__(self,
                 symbol: str,
                 current_time: DATETIME_TYPE,
                 inter_day_look_back: pd.DataFrame,
                 intra_day_look_back: pd.DataFrame) -> None:
        self.symbol = symbol
        self.current_time = current_time
        self.inter_day_look_back = inter_day_look_back
        self.intra_day_look_back = intra_day_look_back

    @property
    def prev_day_close(self) -> float:
        return self.inter_day_look_back.iloc[-1]['Close']
