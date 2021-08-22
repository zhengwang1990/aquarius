from .common import *
import numpy as np
import pandas as pd
import ta.momentum as momentum

_FEATURES = [
    'date',
    'symbol',
    'entry_time',
    'exit_time',
    'side',
    'profit',
    'yesterday_change',
    'change_1_month',
    'std_1_month',
    'true_range_1_month',
    'rsi_14_window',
    'pre_market_change',
    'today_change',
    'prev_window_change',
]


class FeatureExtractor:

    def __init__(self):
        self.data = []

    def extract(self, day: DATETIME_TYPE, symbol: str, entry_time: datetime.time, exit_time: datetime.time,
                side: str, entry_price: float, exit_price: float,
                intraday_lookback: pd.DataFrame, interday_lookback: pd.DataFrame) -> None:
        profit = exit_price / entry_price - 1
        if side == 'short':
            profit *= -1
        interday_closes = interday_lookback['Close']
        prev_close = interday_closes[-1]
        yesterday_change = prev_close / interday_closes[-2] - 1
        change_1_month = interday_closes[-1] / interday_closes[-DAYS_IN_A_MONTH] - 1

        changes = interday_closes[-DAYS_IN_A_MONTH:]
        std_1_month = np.std(changes) if len(changes) else 0

        atrp = []
        for i in range(-DAYS_IN_A_MONTH + 1, 0):
            h = interday_lookback['High'][i]
            l = interday_lookback['Low'][i]
            c = interday_lookback['Close'][i - 1]
            atrp.append(max(h - l, h - c, c - l) / c)
        true_range_1_month = np.average(atrp) if len(atrp) else 0

        intraday_closes = intraday_lookback['Close']
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        if p is None:
            return

        rsi_14_window = momentum.rsi(intraday_closes, window=14).values[-1]

        pre_market_change = 0
        if p > 0:
            pre_market_change = intraday_closes[p - 1] / prev_close - 1

        today_change = intraday_closes[-1] / prev_close - 1

        prev_window_change = intraday_closes[-1] / intraday_closes[-2] - 1

        data = [day, symbol, entry_time, exit_time, side, profit, yesterday_change,
                change_1_month, std_1_month, true_range_1_month, rsi_14_window,
                pre_market_change, today_change, prev_window_change]
        self.data.append(data)

    def save(self, data_path: str):
        df = pd.DataFrame(self.data, columns=_FEATURES)
        df.to_csv(data_path, index=False)
