from typing import Optional
import collections
import datetime
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


def timestamp_to_index(index: pd.Index, timestamp) -> Optional[int]:
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


class DataCollector:

    def __init__(self):
        self._intraday_loader = HistoricalDataLoader(TimeInterval.FIVE_MIN, _DATA_SOURCE)
        self._interday_loader = HistoricalDataLoader(TimeInterval.DAY, _DATA_SOURCE)
        self._columns = ['date']
        for i in range(1, _TRAINING_DAYS + 1):
            for j in range(1, 4):
                self._columns.append(f'inter_{i}_{j}')
        for i in range(1, 68):
            for j in range(1, 3):
                self._columns.append(f'intra_{i}_{j}')
        self._columns.append('label')

    def write_data(self, symbol: str, start_date: str, end_date: str, output_file: str):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        history_start = start_date - datetime.timedelta(days=365)
        interday_data = self._interday_loader.load_data_list(symbol, history_start, end_date)
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=start_date, end_date=end_date - datetime.timedelta(days=1))
        market_dates = [pd.to_datetime(d.date()) for d in mcal.date_range(schedule, frequency='1D')]
        first_day_index = timestamp_to_index(interday_data.index, market_dates[0])

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
            start_index = timestamp_to_index(intraday_data.index, intraday_start)
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
        df.to_csv(output_file, index=False)


def main():
    collector = DataCollector()
    symbol = 'TQQQ'
    start_date = '2020-01-01'
    end_date = '2021-01-01'
    output_file = os.path.join(_ML_ROOT, 'data', '_'.join([symbol, start_date, end_date]) + '.csv')
    collector.write_data(symbol, start_date, end_date, output_file)


if __name__ == '__main__':
    main()
