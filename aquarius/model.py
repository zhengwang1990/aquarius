from .common import *
from sklearn import ensemble
from sklearn import metrics
from tabulate import tabulate
from typing import Optional
import numpy as np
import pandas as pd


def _get_data(df: pd.DataFrame,
              start_date: Optional[DATETIME_TYPE] = None,
              end_date: Optional[DATETIME_TYPE] = None):
    X, Y, W = [], [], []
    for _, row in df.iterrows():
        if start_date is not None and pd.to_datetime(row['date']) < start_date:
            continue
        if end_date is not None and pd.to_datetime(row['date']) > end_date:
            continue
        side = 1 if row['side'] == 'long' else 0
        std_1_month = row['std_1_month']
        normalized_yesterday_change = row['yesterday_change'] / std_1_month
        normalized_change_1_month = row['change_1_month'] / std_1_month
        rsi_14_window = row['rsi_14_window']
        normalized_pre_market_change = row['pre_market_change'] / std_1_month
        normalized_today_change = row['today_change'] / std_1_month
        normalized_prev_window_change = row['prev_window_change'] / std_1_month
        x = [side, normalized_yesterday_change, normalized_change_1_month, normalized_pre_market_change, rsi_14_window,
             normalized_today_change, normalized_prev_window_change]
        y = 1 if row['profit'] > 0 else 0
        w = np.abs(row['profit'])
        X.append(x)
        Y.append(y)
        W.append(w)
    return np.array(X), np.array(Y), np.array(W)


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
        X, Y, W = _get_data(df, start_date, end_date)
        self._model = _create_model()
        self._model.fit(X, Y, W)
        Y_pred = self._model.predict(X)
        #_print_metrics(Y, Y_pred)

    def evaluate(self, data_path: str,
                 start_date: Optional[DATETIME_TYPE] = None,
                 end_date: Optional[DATETIME_TYPE] = None):
        df = pd.read_csv(data_path)
        profits = df['profit']
        X, Y, _ = _get_data(df, start_date, end_date)
        Y_pred = self._model.predict(X)
        _print_metrics(Y, Y_pred)
        asset = 1
        for y, p in zip(Y, profits):
            if y == 1:
                asset *= 1 + p
        print(f'Gain/Loss: {(asset - 1) * 100:.2f}%')
        return asset - 1
