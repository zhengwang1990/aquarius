from enum import Enum


POLYGON_API_KEY = 'POLYGON_API_KEY'


class TimeInterval(Enum):
    FIVE_MIN = 1
    HOUR = 2
    DAY = 3


class DataSource(Enum):
    POLYGON = 1
    YAHOO = 2
