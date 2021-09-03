from .common import *
from datetime import datetime
from sklearn import ensemble
from sklearn import metrics
from tabulate import tabulate
from typing import Optional
import numpy as np
import pandas as pd


def _get_data(df: pd.DataFrame,
              start_date: Optional[DATETIME_TYPE] = None,
              end_date: Optional[DATETIME_TYPE] = None):
    META, X, Y, W, P = [], [], [], [], []
    for _, row in df.iterrows():
        if start_date is not None and pd.to_datetime(row['date']) < start_date:
            continue
        if end_date is not None and pd.to_datetime(row['date']) > end_date:
            continue
        side = 1 if row['side'] == 'long' else 0
        entry_time = datetime.strptime(row['entry_time'], '%H:%M:%S').hour
        std_1_month = row['std_1_month']
        normalized_yesterday_change = row['yesterday_change'] / std_1_month
        normalized_change_5_day = row['change_5_day'] / std_1_month
        normalized_change_1_month = row['change_1_month'] / std_1_month
        normalized_change_1_month_low = row['change_1_month_low'] / std_1_month
        normalized_change_1_month_high = row['change_1_month_high'] / std_1_month
        #normalized_current_change_today = row['current_change_today'] / std_1_month
        #normalized_current_change_2_day = row['current_change_2_day'] / std_1_month
        normalized_current_change_today_low = row['current_change_today_low'] / std_1_month
        normalized_current_change_today_high = row['current_change_today_high'] / std_1_month

        dollar_volume = row['dollar_volume']
        rsi_14_window = row['rsi_14_window']
        rsi_14_window_prev1 = row['rsi_14_window_prev1']
        #rsi_14_window_prev2 = row['rsi_14_window_prev2']
        normalized_pre_market_change = row['pre_market_change'] / std_1_month
        normalized_prev_window_change = row['prev_window_change'] / std_1_month
        true_range_1_month = row['true_range_1_month']
        current_volume_change = row['current_volume_change']
        #prev_volume_change = row['prev_volume_change']

        x = [side, entry_time, normalized_yesterday_change, normalized_change_5_day, normalized_change_1_month,
             normalized_change_1_month_low, normalized_change_1_month_high,
             normalized_current_change_today_low, normalized_current_change_today_high,
             normalized_pre_market_change, dollar_volume, rsi_14_window, rsi_14_window_prev1,
             normalized_prev_window_change, true_range_1_month, current_volume_change]
        p = row['profit']
        y = 1 if p > 0 else 0
        w = np.abs(p)
        X.append(x)
        Y.append(y)
        W.append(w)
        P.append(p)
        META.append((row['date'], row['symbol']))
    return np.array(X), np.array(Y), np.array(W), np.array(P), META


def _create_model():
    hyper_parameters = {'max_depth': 5,
                        'min_samples_leaf': 1,
                        'n_jobs': -1,
                        'random_state': 0}
    return ensemble.RandomForestClassifier(**hyper_parameters)


def _print_metrics(Y, Y_pred):
    confusion_matrix_main = metrics.confusion_matrix(Y, Y_pred, labels=[0, 1])
    confusion_table_main = [['', 'Predict Lose', 'Predict Win'],
                            ['True Lose', confusion_matrix_main[0][0], confusion_matrix_main[0][1]],
                            ['True Win', confusion_matrix_main[1][0], confusion_matrix_main[1][1]]]
    print(tabulate(confusion_table_main, tablefmt='grid'))


class Model:

    def __init__(self):
        self._model = None

    def train(self,
              data_path: str,
              start_date: Optional[DATETIME_TYPE] = None,
              end_date: Optional[DATETIME_TYPE] = None):
        df = pd.read_csv(data_path)
        X, Y, W, _, _ = _get_data(df, start_date, end_date)
        self._model = _create_model()
        self._model.fit(X, Y, W)
        #Y_pred = self._model.predict(X)
        #_print_metrics(Y, Y_pred)

    def evaluate(self, data_path: str,
                 start_date: Optional[DATETIME_TYPE] = None,
                 end_date: Optional[DATETIME_TYPE] = None):
        df = pd.read_csv(data_path)
        X, Y, _, P, META = _get_data(df, start_date, end_date)
        Y_pred = self._model.predict(X)
        _print_metrics(Y, Y_pred)
        asset = 1
        for y, p, meta in zip(Y_pred, P, META):
            if y == 1:
                asset *= 1 + p
        print(f'Gain/Loss: {(asset - 1) * 100:.2f}%')
        return asset - 1
