from enum import Enum
import collections
import os

POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY')

TIME_ZONE = 'US/Eastern'

CACHE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'cache')


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
    pass
