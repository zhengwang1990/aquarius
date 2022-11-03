import collections
import datetime
import inspect
import logging
import os
import sys
from enum import Enum
from typing import List, Optional, Union

import pandas as pd
import pytz

TIME_ZONE = pytz.timezone('America/New_York')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
DATETIME_TYPE = Union[pd.Timestamp, pd.DatetimeIndex, datetime.datetime]
DAYS_IN_A_WEEK = 5
DAYS_IN_A_MONTH = 20
CALENDAR_DAYS_IN_A_MONTH = 35
CALENDAR_DAYS_IN_A_YEAR = 365
DAYS_IN_A_QUARTER = 60
DAYS_IN_A_YEAR = 250
MARKET_OPEN = datetime.time(9, 30)
MARKET_CLOSE = datetime.time(16, 0)
SHORT_RESERVE_RATIO = 1
EPSILON = 1E-7
INTERDAY_LOOKBACK_LOAD = CALENDAR_DAYS_IN_A_YEAR
BID_ASK_SPREAD = 0.001


class TimeInterval(Enum):
    FIVE_MIN = 1
    HOUR = 2
    DAY = 3

    def __str__(self):
        return self.name


class DataSource(Enum):
    POLYGON = 1
    ALPACA = 2

    def __str__(self):
        return self.name


class ActionType(Enum):
    BUY_TO_OPEN = 1
    SELL_TO_OPEN = 2
    BUY_TO_CLOSE = 3
    SELL_TO_CLOSE = 4

    def __str__(self):
        return self.name


class Mode(Enum):
    BACKTEST = 1
    TRADE = 2

    def __str__(self):
        return self.name


class TradingFrequency(Enum):
    FIVE_MIN = 1
    CLOSE_TO_CLOSE = 2
    CLOSE_TO_OPEN = 3

    def __str__(self):
        return self.name


ProcessorAction = collections.namedtuple('ProcessorAction', ['symbol', 'type', 'percent'], defaults=(1,))
Action = collections.namedtuple('Action', ['symbol', 'type', 'percent', 'price', 'processor'])
Position = collections.namedtuple('Position', ['symbol', 'qty', 'entry_price', 'entry_time'])
DEFAULT_DATA_SOURCE = DataSource.ALPACA


def timestamp_to_index(index: pd.Index, timestamp: DATETIME_TYPE) -> Optional[int]:
    pd_timestamp = pd.to_datetime(timestamp).timestamp()
    left, right = 0, len(index) - 1
    while left <= right:
        mid = (left + right) // 2
        mid_timestamp = pd.to_datetime(index[mid]).timestamp()
        if mid_timestamp == pd_timestamp:
            return mid
        elif mid_timestamp < pd_timestamp:
            left = mid + 1
        else:
            right = mid - 1
    return None


def timestamp_to_prev_index(index: pd.Index, timestamp: DATETIME_TYPE) -> Optional[int]:
    if len(index) == 0:
        return None
    p = len(index) - 1
    pd_timestamp = pd.to_datetime(timestamp).timestamp()
    for i in range(len(index)):
        if pd.to_datetime(index[i]).timestamp() > pd_timestamp:
            p = i - 1
            break
    return p


def get_unique_actions(actions: List[Action]) -> List[Action]:
    action_sets = set([(action.symbol, action.type) for action in actions])
    unique_actions = []
    for unique_action in action_sets:
        similar_actions = [action for action in actions if (action.symbol, action.type) == unique_action]
        action = similar_actions[0]
        for i in range(1, len(similar_actions)):
            if similar_actions[i].percent > action.percent:
                action = similar_actions[i]
        unique_actions.append(action)
    unique_actions.sort(key=lambda action: action.symbol)
    return unique_actions


def logging_config(logging_file=None, detail=True, name=None) -> logging.Logger:
    """Configuration for logging."""
    logger = logging.getLogger(name=name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    if detail:
        formatter = logging.Formatter(
            '[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s')
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
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def get_header(title):
    header_left = '== [ %s ] ' % (title,)
    return header_left + '=' * (80 - len(header_left))


class Context:

    def __init__(self,
                 symbol: str,
                 current_time: DATETIME_TYPE,
                 current_price: float,
                 interday_lookback: pd.DataFrame,
                 intraday_lookback: Optional[pd.DataFrame],
                 mode: Optional[Mode] = None) -> None:
        self.symbol = symbol
        self.current_time = current_time
        self.current_price = current_price
        self.interday_lookback = interday_lookback
        self.intraday_lookback = intraday_lookback
        self.mode = mode

    @property
    def prev_day_close(self) -> float:
        return self.interday_lookback['Close'][-1]

    @property
    def vwap(self) -> List[float]:
        res = []
        vwaps = self.intraday_lookback['VWAP']
        volumes = self.intraday_lookback['Volume']
        total_dolloar = 0
        total_volume = 0
        for i in range(len(self.intraday_lookback)):
            total_dolloar += vwaps[i] * volumes[i]
            total_volume += volumes[i]
            res.append(total_dolloar / (total_volume + 1E-7))
        return res

    @property
    def market_open_index(self) -> Optional[int]:
        for i in range(len(self.intraday_lookback)):
            if self.intraday_lookback.index[i].time() >= MARKET_OPEN:
                return i
        return None

    @property
    def today_open(self) -> float:
        p = self.market_open_index
        return self.intraday_lookback['Open'][p] if p is not None else None


class Processor:

    def __init__(self) -> None:
        return

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        raise NotImplementedError('Calling parent interface')

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        return None

    def process_all_data(self, contexts: List[Context]) -> List[ProcessorAction]:
        actions = []
        for context in contexts:
            action = self.process_data(context)
            if action:
                actions.append(action)
        return actions

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        return

    def teardown(self) -> None:
        return

    def get_trading_frequency(self) -> TradingFrequency:
        raise NotImplementedError('Calling parent interface')


class ProcessorFactory:

    def __init__(self) -> None:
        self._source_file = inspect.getfile(self.__class__)
        create_signature = inspect.signature(self.create)
        processor_class = create_signature.return_annotation
        # Check if processor class is written in the same file as factory class
        assert inspect.getfile(processor_class) == self._source_file

    def create(self, *args, **kwargs) -> Processor:
        raise NotImplementedError('Calling parent interface')

    def snapshot(self, output_dir: str) -> None:
        snapshot_file = os.path.join(output_dir, os.path.basename(self._source_file))
        with open(snapshot_file, 'w') as f_snapshot:
            with open(self._source_file, 'r') as f_source:
                f_snapshot.write(f_source.read())


def get_processor_name(processor: Processor) -> str:
    processor_name = type(processor).__name__
    suffix = 'Processor'
    assert processor_name.endswith(suffix)
    return processor_name[:-len(suffix)]
