from enum import Enum
import collections
import os

POLYGON_API_KEY = 'POLYGON_API_KEY'

TIME_ZONE = 'US/Eastern'

CACHE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'cache')


class TimeInterval(Enum):
    FIVE_MIN = 1
    HOUR = 2
    DAY = 3


class DataSource(Enum):
    POLYGON = 1
    YAHOO = 2


class DataError(Exception):
    pass


DataPoint = collections.namedtuple('DataPoint', ['o', 'h', 'l', 'c', 'v', 't'])
