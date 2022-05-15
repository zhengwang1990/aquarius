from typing import Optional
import collections
import datetime
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import os
import sys
import tqdm

sys.path.append('../alpharius')
from alpharius import *

_ML_ROOT = os.path.dirname(os.path.realpath(__file__))
_TIME_ZONE = 'America/New_York'
_DATA_SOURCE = DataSource.ALPACA
_MARKET_START = datetime.time(9, 30)
_COLLECT_START = datetime.time(10, 0)
_COLLECT_END = datetime.time(15, 0)
_TRAINING_DAYS = 240

Data = collections.namedtuple('Dataset', ['name', 'train_data', 'test_data', 'test_data_raw'],
                              defaults=[None])


def _timestamp_to_index(index: pd.Index, timestamp) -> Optional[int]:
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


def _get_row(prefix, d1, d2, data_row):
    row = []
    for f1 in range(1, d1 + 1):
        pt = []
        for f2 in range(1, d2 + 1):
            feature_name = f'{prefix}_{f1}_{f2}'
            pt.append(data_row[feature_name] * 100)
        row.append(np.array(pt))
    return np.array(row)


class Dataset:

    def __init__(self, symbol: str, start_date: str, end_date: str):
        self._intraday_loader = HistoricalDataLoader(TimeInterval.FIVE_MIN, _DATA_SOURCE)
        self._interday_loader = HistoricalDataLoader(TimeInterval.DAY, _DATA_SOURCE)
        self._columns = ['date']
        self._inter_d1, self._inter_d2 = _TRAINING_DAYS, 3
        self._intra_d1, self._intra_d2 = 67, 2
        for i in range(1, self._inter_d1 + 1):
            for j in range(1, self._inter_d2 + 1):
                self._columns.append(f'inter_{i}_{j}')
        for i in range(1, self._intra_d1 + 1):
            for j in range(1, self._intra_d2 + 1):
                self._columns.append(f'intra_{i}_{j}')
        self._columns.append('label')
        self._data = self._download_data(symbol, start_date, end_date)
        curr_month = self._data['date'].iloc[0][:7]
        self._months = [(curr_month, 0)]
        for i, d in enumerate(self._data['date']):
            if d[:7] != curr_month:
                curr_month = d[:7]
                self._months.append((curr_month, i))
        self._months.append(('', len(self._data['date'])))

    def _download_data(self, symbol: str, start_date: str, end_date: str):
        data_file = f'{symbol}_{start_date}_{end_date}.csv'
        data_path = os.path.join(_ML_ROOT, 'data', data_file)
        if os.path.exists(data_path):
            return pd.read_csv(data_path)

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        history_start = start_date - datetime.timedelta(days=365)
        interday_data = self._interday_loader.load_data_list(symbol, history_start, end_date)
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=start_date, end_date=end_date - datetime.timedelta(days=1))
        market_dates = [pd.to_datetime(d.date()) for d in mcal.date_range(schedule, frequency='1D')]
        first_day_index = _timestamp_to_index(interday_data.index, market_dates[0])

        interday_close = interday_data['Close']
        interday_open = interday_data['Open']
        interday_queue = collections.deque([0, 0, 0])
        for i in range(first_day_index - _TRAINING_DAYS + 1, first_day_index):
            interday_queue.append(interday_close[i - 1] / interday_open[i - 1] - 1)
            interday_queue.append(interday_close[i - 1] / interday_close[i - 2] - 1)
            interday_queue.append(interday_open[i - 1] / interday_close[i - 2] - 1)
        output_data = []
        for i in tqdm.tqdm(range(first_day_index, len(interday_data)), ncols=80):
            for _ in range(3):
                interday_queue.popleft()
            interday_queue.append(interday_close[i - 1] / interday_open[i - 1] - 1)
            interday_queue.append(interday_close[i - 1] / interday_close[i - 2] - 1)
            interday_queue.append(interday_open[i - 1] / interday_close[i - 2] - 1)

            current_day = interday_data.index[i]
            intraday_start = pd.to_datetime(
                pd.Timestamp.combine(current_day.date(), _COLLECT_START)).tz_localize(_TIME_ZONE)
            intraday_data = self._intraday_loader.load_daily_data(symbol, current_day)
            start_index = _timestamp_to_index(intraday_data.index, intraday_start)
            if start_index is None:
                continue
            end_index = start_index + 60
            if len(interday_data) < end_index or intraday_data.index[end_index].time() != _COLLECT_END:
                continue
            market_start = start_index - 6
            if market_start < 0 or intraday_data.index[market_start].time() != _MARKET_START:
                continue

            intraday_close = intraday_data['Close']
            intraday_queue = collections.deque([0] * ((end_index - market_start + 1) * 2))
            for j in range(market_start, end_index + 1):
                for _ in range(2):
                    intraday_queue.popleft()
                intraday_queue.append(intraday_close[j] / intraday_close[j - 1] - 1)
                intraday_queue.append(intraday_close[j] / interday_close[i - 1] - 1)
                if j >= start_index:
                    label = interday_close[i] / intraday_close[j] - 1
                    row_data = [str(current_day.strftime('%F'))] + list(interday_queue) + list(intraday_queue)
                    row_data.append(label)
                    output_data.append(row_data)
        df = pd.DataFrame(output_data, columns=self._columns)

        df.to_csv(data_path, index=False)
        return df

    def get_data(self, start_month_idx: int, end_month_idx: int):
        start_data_idx = self._months[start_month_idx][1]
        end_data_idx = self._months[end_month_idx][1]
        inter_data = []
        intra_data = []
        labels = []
        for i in range(start_data_idx, end_data_idx):
            data_row = self._data.iloc[i]
            inter_row = _get_row('inter', self._inter_d1, self._inter_d2, data_row)
            intra_row = _get_row('intra', self._intra_d1, self._intra_d2, data_row)
            label = data_row['label']
            if label > 5E-3:
                label = 1
            elif label < -5E-3:
                label = -1
            else:
                label = 0
            inter_data.append(inter_row)
            intra_data.append(intra_row)
            labels.append(label)
        return [np.array(inter_data), np.array(intra_data)], np.array(labels)

    def get_train_test(self):
        for i in range(0, len(self._months) - 13):
            train_data = self.get_data(i, i + 12)
            test_data = self.get_data(i + 12, i + 13)
            yield Data(name=self._months[i + 12][0],
                       train_data=train_data, test_data=test_data)

    def get_month_size(self):
        return len(self._months)
