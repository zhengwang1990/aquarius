from alpharius.common import *
from alpharius.data import HistoricalDataLoader
from dateutil import relativedelta
from typing import Optional
import collections
import datetime
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import tqdm

_DATA_SOURCE = DataSource.ALPACA
_MARKET_START = datetime.time(9, 30)
_COLLECT_START = datetime.time(10, 0)
_COLLECT_END = datetime.time(15, 30)
_COLLECT_SKIP = (_COLLECT_START.hour * 60 + _COLLECT_START.minute - _MARKET_START.hour * 60 - _MARKET_START.minute) // 5
_LABEL_SKIP = 6
_DATA_WINDOW_MONTH = 12
INTRADAY_DIM = (_COLLECT_END.hour * 60 + _COLLECT_END.minute - _MARKET_START.hour * 60 - _MARKET_START.minute) // 5
INTERDAY_DIM = 240

Data = collections.namedtuple('Dataset', ['name', 'train_data', 'test_data'])


class Dataset:

    def __init__(self):
        pass

    @staticmethod
    def get_interday_input(interday_data: pd.DataFrame, current_index: int = None) -> np.ndarray:
        current_index = current_index or len(interday_data) - 1
        assert current_index >= INTERDAY_DIM - 1
        interday_close = interday_data['Close']
        interday_open = interday_data['Open']
        output = []
        for i in range(current_index - INTERDAY_DIM + 1, current_index + 1):
            data_point = [
                (interday_close[i - 1] / interday_open[i - 1] - 1) * 100,
                (interday_close[i - 1] / interday_close[i - 2] - 1) * 100,
                (interday_open[i - 1] / interday_close[i - 2] - 1) * 100,
            ]
            output.append(np.asarray(data_point, dtype=np.float32))
        return np.asarray(output, dtype=np.float32)

    @staticmethod
    def get_intraday_input(intraday_data: pd.DataFrame,
                           prev_day_close: float,
                           current_index: int = None) -> np.ndarray:
        current_index = current_index or len(intraday_data) - 1
        market_start_index = 0
        while (market_start_index < len(intraday_data) and
               intraday_data.index[market_start_index].time() < _MARKET_START):
            market_start_index += 1
        intraday_close = intraday_data['Close']
        intraday_open = intraday_data['Open']
        output = []
        for i in range(market_start_index, current_index + 1):
            data_point = [
                (intraday_close[i] / intraday_open[i] - 1) * 100,
                (intraday_close[i] / prev_day_close - 1) * 100,
            ]
            output.append(np.asarray(data_point, dtype=np.float32))
        if len(output) > INTRADAY_DIM:
            output = output[-INTRADAY_DIM:]
        else:
            output = [np.asarray([0, 0], dtype=np.float32)] * (INTRADAY_DIM - len(output)) + output
        return np.asarray(output, dtype=np.float32)

    @staticmethod
    def get_label(intraday_data: pd.DataFrame,
                  current_index: int) -> Optional[float]:
        intraday_close = intraday_data['Close']
        if current_index + _LABEL_SKIP >= len(intraday_close):
            return None
        profit = intraday_close[current_index + _LABEL_SKIP] / intraday_close[current_index] - 1
        if profit > 3E-3:
            return 1
        elif profit < -3E-3:
            return -1
        else:
            return 0

    def _prepare_data(self, symbol: str, start_date: str, end_date: str):
        interday_loader = HistoricalDataLoader(TimeInterval.DAY, _DATA_SOURCE)
        intraday_loader = HistoricalDataLoader(TimeInterval.FIVE_MIN, _DATA_SOURCE)
        collection_start = pd.to_datetime(start_date) - relativedelta.relativedelta(months=_DATA_WINDOW_MONTH)
        collection_end = pd.to_datetime(end_date)
        history_start = collection_start - datetime.timedelta(days=365)
        interday_data = interday_loader.load_data_list(symbol, history_start, collection_end)
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=collection_start, end_date=collection_end - datetime.timedelta(days=1))
        market_dates = [pd.to_datetime(d.date()) for d in mcal.date_range(schedule, frequency='1D')]
        first_day_index = timestamp_to_index(interday_data.index, market_dates[0])
        interday_close = interday_data['Close']

        indices = []
        interday_inputs = []
        intraday_inputs = []
        labels = []

        for i in tqdm.tqdm(range(first_day_index, len(interday_data)), ncols=80):
            interday_input = self.get_interday_input(interday_data, i)
            current_day = interday_data.index[i]
            intraday_start = pd.to_datetime(
                pd.Timestamp.combine(current_day.date(), _COLLECT_START)).tz_localize(TIME_ZONE)
            intraday_data = intraday_loader.load_daily_data(symbol, current_day)
            start_index = timestamp_to_index(intraday_data.index, intraday_start)
            if start_index is None:
                continue
            market_start = start_index - _COLLECT_SKIP
            if market_start < 0 or intraday_data.index[market_start].time() != _MARKET_START:
                continue
            end_index = market_start + INTRADAY_DIM
            if len(intraday_data) <= end_index or intraday_data.index[end_index].time() != _COLLECT_END:
                continue

            for j in range(start_index, end_index):
                intraday_input = self.get_intraday_input(intraday_data, interday_close[i - 1], j)
                label = self.get_label(intraday_data, j)
                if label is None:
                    continue
                indices.append(interday_close.index[i])
                interday_inputs.append(interday_input)
                intraday_inputs.append(intraday_input)
                labels.append(label)

        return (indices, np.asarray(interday_inputs, dtype=np.float32),
                np.asarray(intraday_inputs, dtype=np.float32), np.asarray(labels, dtype=np.int))

    @staticmethod
    def get_index_offset(indices: List[pd.DatetimeIndex]):
        curr_month = indices[0].strftime('%Y-%m')
        offsets = [(curr_month, 0)]
        for i, d in enumerate(indices):
            month = d.strftime('%Y-%m')
            if month != curr_month:
                curr_month = month
                offsets.append((curr_month, i))
        next_month = indices[-1] + relativedelta.relativedelta(month=1)
        offsets.append((next_month.strftime('%Y-%m'), len(indices)))
        return offsets

    def train_test_iterator(self, symbol: str, start_date: str, end_date: str):
        indices, interday_inputs, intraday_inputs, labels = self._prepare_data(symbol, start_date, end_date)
        offsets = self.get_index_offset(indices)
        for i in range(0, len(offsets) - _DATA_WINDOW_MONTH - 1):
            train_start = offsets[i][1]
            train_end = test_start = offsets[i + _DATA_WINDOW_MONTH][1]
            test_end = offsets[i + _DATA_WINDOW_MONTH + 1][1]
            train_data = ([interday_inputs[train_start:train_end], intraday_inputs[train_start:train_end]],
                          labels[train_start:train_end])
            test_data = ([interday_inputs[test_start:test_end], intraday_inputs[test_start:test_end]],
                         labels[test_start:test_end])
            yield Data(name=offsets[i + _DATA_WINDOW_MONTH][0],
                       train_data=train_data, test_data=test_data)

    def train_iterator(self, symbol: str, start_date: str, end_date: str):
        indices, interday_inputs, intraday_inputs, labels = self._prepare_data(symbol, start_date, end_date)
        offsets = self.get_index_offset(indices)
        for i in range(0, len(offsets) - _DATA_WINDOW_MONTH):
            train_start = offsets[i][1]
            train_end = offsets[i + _DATA_WINDOW_MONTH][1]
            train_data = ([interday_inputs[train_start:train_end], intraday_inputs[train_start:train_end]],
                          labels[train_start:train_end])
            yield Data(name=offsets[i + _DATA_WINDOW_MONTH][0], train_data=train_data, test_data=None)
