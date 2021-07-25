from enum import Enum
from typing import Union
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


class DataError(Exception):
    """Error in data loading."""
