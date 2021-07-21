from enum import Enum
import collections

POLYGON_API_KEY = 'POLYGON_API_KEY'


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
