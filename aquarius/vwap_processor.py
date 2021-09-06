from .common import *
from .stock_universe import StockUniverse
from dateutil.relativedelta import relativedelta
from sklearn import ensemble, metrics
from typing import List, Optional
from tabulate import tabulate
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pickle
import ta.momentum as momentum

_WATCHING_WINDOW = 12

_FEATURES = [
    'date',
    'symbol',
    'entry_time',
    'side',
    'yesterday_change',
    'change_5_day',
    'change_1_month',
    'change_1_month_low',
    'change_1_month_high',
    'current_change_today',
    'current_change_2_day',
    'current_change_today_low',
    'current_change_today_high',
    'std_1_month',
    'true_range_1_month',
    'dollar_volume',
    'rsi_14_window',
    'rsi_14_window_prev1',
    'rsi_14_window_prev2',
    'pre_market_change',
    'prev_window_change',
    'current_volume_change',
    'current_candle_top_portion',
    'current_candle_middle_portion',
    'current_candle_bottom_portion',
    'prev_volume_change',
    'prev_candle_top_portion',
    'prev_candle_middle_portion',
    'prev_candle_bottom_portion',
    'current_change_since_open',
]

_LABELS = ['exit_time', 'profit']


class VwapProcessor(Processor):

    def __init__(self,
                 lookback_start_date: DATETIME_TYPE,
                 lookback_end_date: DATETIME_TYPE,
                 data_source: DataSource,
                 enable_model: bool = False) -> None:
        super().__init__()
        self._stock_universe = VwapStockUniverse(start_time=lookback_start_date,
                                                 end_time=lookback_end_date,
                                                 data_source=data_source)
        self._stock_universe.set_dollar_volume_filter(low=1E7)
        self._stock_universe.set_average_true_range_percent_filter(low=0.01)
        self._stock_universe.set_price_filer(low=1)
        self._hold_positions = {}
        self._feature_extractor = VwapFeatureExtractor()
        self._enable_model = enable_model
        self._models = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_universe.get_stock_universe(view_time)

    def process_data(self, context: Context) -> Optional[Action]:
        if context.symbol in self._hold_positions:
            return self._close_position(context)
        return self._open_position(context)

    def _open_position(self, context: Context) -> Optional[Action]:
        if (context.current_time.time() >= datetime.time(15, 0)
                or context.current_time.time() <= datetime.time(10, 00)):
            return
        intraday_lookback = context.intraday_lookback
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        if p is None:
            return
        intraday_closes = intraday_lookback['Close'][p:]
        if len(intraday_closes) < _WATCHING_WINDOW:
            return

        vwap = context.vwap
        vwap_distances = []
        for i in range(1, _WATCHING_WINDOW + 1):
            vwap_distances.append(intraday_closes[-i] - vwap[-i])

        distance_sign = np.sign(vwap_distances[0])
        if np.sign(vwap_distances[1]) != distance_sign:
            return
        for distance in vwap_distances[2:]:
            if np.sign(distance) == distance_sign:
                return

        if distance_sign > 0:
            side = 'long'
            action_type = ActionType.BUY_TO_OPEN
        else:
            side = 'short'
            action_type = ActionType.SELL_TO_OPEN

        intraday_low = np.min(intraday_lookback['Low'])
        intraday_high = np.max(intraday_lookback['High'])
        intraday_range = intraday_high - intraday_low

        if np.abs(context.current_price - vwap[-1]) > min(0.01 * context.current_price, 0.1 * intraday_range):
            return

        interday_closes = context.interday_lookback['Close']
        if len(interday_closes) < 2:
            return
        if side == 'long':
            if context.prev_day_close < interday_closes[-2]:
                return
        if side == 'short':
            if context.prev_day_close > interday_closes[-2]:
                return

        feature = self._feature_extractor.extract_feature(context.symbol,
                                                          context.current_time,
                                                          context.current_time.time(),
                                                          side,
                                                          context.current_price,
                                                          context.intraday_lookback,
                                                          context.interday_lookback)

        if self._enable_model:
            model = self._get_model(context.current_time)
            y = model.predict(feature)
            if y[0] == 0:
                return
        self._hold_positions[context.symbol] = {'side': side,
                                                'entry_time': context.current_time,
                                                'entry_price': context.current_price,
                                                'feature': feature}
        return Action(context.symbol, action_type, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        def _pop_position():
            self._hold_positions.pop(symbol)
            self._feature_extractor.extract_data(feature, entry_price, current_price,
                                                 context.current_time.time(), side)
            return action

        symbol = context.symbol
        position = self._hold_positions[symbol]
        entry_time = position['entry_time']
        prev_close = context.intraday_lookback['Close'][-1]
        prev_open = context.intraday_lookback['Open'][-1]
        current_price = context.current_price
        entry_price = position['entry_price']
        feature = position['feature']
        side = position['side']
        if side == 'long':
            action = Action(symbol, ActionType.SELL_TO_CLOSE, 1, current_price)
            if current_price < context.vwap[-1] and current_price < entry_price * 0.995:
                return _pop_position()
            if current_price > entry_price * 1.01 and prev_close < prev_open:
                return _pop_position()
        else:
            action = Action(symbol, ActionType.BUY_TO_CLOSE, 1, current_price)
            if current_price > context.vwap[-1] and current_price > entry_price * 1.005:
                return _pop_position()
            if current_price < entry_price * 0.99 and prev_close > prev_open:
                return _pop_position()
        if (context.current_time - entry_time >= datetime.timedelta(hours=1) or
                context.current_time.time() >= datetime.time(15, 55)):
            return _pop_position()

    def _get_model(self, current_time: DATETIME_TYPE):
        model_path = os.path.join(MODEL_ROOT, current_time.strftime('vwap-%Y-%m.pickle'))
        if model_path not in self._models:
            model = VwapModel()
            model.load(model_path)
            self._models[model_path] = model
        return self._models[model_path]

    def teardown(self, output_dir: Optional[str] = None) -> None:
        if output_dir is not None:
            path = os.path.join(output_dir, 'vwap_data.csv')
            self._feature_extractor.save(path)


class VwapProcessorFactory(ProcessorFactory):

    def __init__(self, enable_model=True):
        super().__init__()
        self._enable_model = enable_model

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> VwapProcessor:
        return VwapProcessor(lookback_start_date, lookback_end_date, data_source, self._enable_model)


class VwapStockUniverse(StockUniverse):

    def __init__(self,
                 start_time: DATETIME_TYPE,
                 end_time: DATETIME_TYPE,
                 data_source: DataSource) -> None:
        super().__init__(start_time, end_time, data_source)

    def get_significant_change(self, symbol: str, prev_day: DATETIME_TYPE) -> bool:
        hist = self._historical_data[symbol]
        p = timestamp_to_index(hist.index, prev_day)
        closes = np.array(hist['Close'][max(p - DAYS_IN_A_MONTH + 1, 1):p + 1])
        changes = np.array([np.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)
                            if closes[i + 1] > 0 and closes[i] > 0])
        if not len(changes):
            return False
        std = np.std(changes)
        mean = np.mean(changes)
        if std < 1E-7:
            return False
        if np.abs((changes[-1] - mean) / std) < 3:
            return False
        return True

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        prev_day = self.get_prev_day(view_time)
        symbols = super().get_stock_universe(view_time)
        res = []
        for symbol in symbols:
            if self.get_significant_change(symbol, prev_day):
                res.append(symbol)
        return res


class VwapFeatureExtractor:

    def __init__(self):
        self._data = []

    @staticmethod
    def extract_feature(symbol: str,
                        day: DATETIME_TYPE,
                        entry_time: datetime.time,
                        side: str,
                        entry_price: float,
                        intraday_lookback: pd.DataFrame,
                        interday_lookback: pd.DataFrame) -> Optional[pd.DataFrame]:
        interday_closes = interday_lookback['Close']
        prev_close = interday_closes[-1]
        yesterday_change = prev_close / interday_closes[-2] - 1
        change_5_day = prev_close / interday_closes[-6] - 1
        change_1_month = prev_close / interday_closes[-DAYS_IN_A_MONTH] - 1
        change_1_month_low = prev_close / np.min(interday_closes[-DAYS_IN_A_MONTH:]) - 1
        change_1_month_high = prev_close / np.max(interday_closes[-DAYS_IN_A_MONTH:]) - 1

        current_change_today = entry_price / prev_close - 1
        current_change_2_day = entry_price / interday_closes[-2] - 1
        current_change_today_low = entry_price / np.min(interday_closes) - 1
        current_change_today_high = entry_price / np.max(interday_closes) - 1

        changes = interday_closes[-DAYS_IN_A_MONTH:]
        std_1_month = np.std(changes) if len(changes) else 0

        atrp = []
        dvol = []
        for i in range(-DAYS_IN_A_MONTH, 0):
            h = interday_lookback['High'][i]
            l = interday_lookback['Low'][i]
            c = interday_lookback['Close'][i - 1]
            atrp.append(max(h - l, h - c, c - l) / c)
            dvol.append(interday_lookback['VWAP'][i] * interday_lookback['Volume'][i])
        true_range_1_month = np.average(atrp) if len(atrp) else 0
        dollar_volume = np.average(dvol) if len(dvol) else 0

        intraday_closes = intraday_lookback['Close']
        intraday_opens = intraday_lookback['Open']
        intraday_volumes = intraday_lookback['Volume']
        intraday_highs = intraday_lookback['Volume']
        intraday_lows = intraday_lookback['Low']
        p = None
        for i in range(len(intraday_lookback)):
            if intraday_lookback.index[i].time() >= MARKET_OPEN:
                p = i
                break
        if p is None:
            return

        rsi = momentum.rsi(intraday_closes, window=14).values
        rsi_14_window = rsi[-1] if len(intraday_closes) >= 14 else 0
        rsi_14_window_prev1 = rsi[-2] if len(intraday_closes) >= 15 else 0
        rsi_14_window_prev2 = rsi[-3] if len(intraday_closes) >= 16 else 0

        pre_market_change = 0
        if p > 0:
            pre_market_change = intraday_closes[p - 1] / prev_close - 1

        prev_window_change = intraday_closes[-1] / intraday_closes[-2] - 1

        current_volume_change = 0
        if len(intraday_volumes) - 1 > p:
            current_volume_change = intraday_volumes[-1] / np.average(intraday_volumes[p:len(intraday_volumes) - 1])
        current_candle_size = intraday_highs[-1] - intraday_lows[-1]
        current_candle_top_portion = (intraday_highs[-1] -
                                      max(intraday_opens[-1], intraday_closes[-1])) / current_candle_size
        current_candle_middle_portion = abs(intraday_opens[-1] - intraday_closes[-1]) / current_candle_size
        current_candle_bottom_portion = (min(intraday_opens[-1], intraday_closes[-1]) -
                                         intraday_lows[-1]) / current_candle_size

        prev_volume_change = 0
        if len(intraday_volumes) - 2 > p:
            prev_volume_change = intraday_volumes[-2] / np.average(intraday_volumes[p:len(intraday_volumes) - 2])
        prev_candle_size = intraday_highs[-2] - intraday_lows[-2]
        prev_candle_top_portion = (intraday_highs[-2] -
                                   max(intraday_opens[-2], intraday_closes[-2])) / prev_candle_size
        prev_candle_middle_portion = abs(intraday_opens[-2] - intraday_closes[-2]) / prev_candle_size
        prev_candle_bottom_portion = (min(intraday_opens[-2], intraday_closes[-2]) -
                                      intraday_lows[-2]) / prev_candle_size

        current_change_since_open = entry_price / intraday_opens[p] - 1

        data = [day.strftime('%F'), symbol,
                entry_time.strftime('%H:%M:%S'),
                side, yesterday_change,
                change_5_day, change_1_month, change_1_month_low, change_1_month_high,
                current_change_today, current_change_2_day,
                current_change_today_low, current_change_today_high,
                std_1_month, true_range_1_month, dollar_volume,
                rsi_14_window, rsi_14_window_prev1, rsi_14_window_prev2,
                pre_market_change, prev_window_change,
                current_volume_change, current_candle_top_portion, current_candle_middle_portion,
                current_candle_bottom_portion, prev_volume_change, prev_candle_top_portion,
                prev_candle_middle_portion, prev_candle_bottom_portion, current_change_since_open]
        return pd.DataFrame([data], columns=_FEATURES)

    def extract_data(self,
                     feature: pd.DataFrame,
                     entry_price: float,
                     exit_price: float,
                     exit_time: datetime.time,
                     side: str) -> None:
        profit = exit_price / entry_price - 1
        if side == 'short':
            profit *= -1
        data = np.concatenate([feature.iloc[0].values, [exit_time.strftime('%H:%M:%S'), profit]])
        self._data.append(data)

    def save(self, data_path: Optional[str]) -> None:
        df = pd.DataFrame(self._data, columns=_FEATURES + _LABELS)
        df.to_csv(data_path, index=False)


class VwapModel:

    def __init__(self):
        self._model = None

    @staticmethod
    def _get_feature(df: pd.DataFrame) -> np.ndarray:
        feature = []
        for _, row in df.iterrows():
            side = 1 if row['side'] == 'long' else 0
            entry_time = datetime.datetime.strptime(row['entry_time'], '%H:%M:%S').hour
            std_1_month = row['std_1_month']
            normalized_yesterday_change = row['yesterday_change'] / std_1_month
            normalized_change_5_day = row['change_5_day'] / std_1_month
            normalized_change_1_month = row['change_1_month'] / std_1_month
            normalized_change_1_month_low = row['change_1_month_low'] / std_1_month
            normalized_change_1_month_high = row['change_1_month_high'] / std_1_month
            # normalized_current_change_today = row['current_change_today'] / std_1_month
            # normalized_current_change_2_day = row['current_change_2_day'] / std_1_month
            normalized_current_change_today_low = row['current_change_today_low'] / std_1_month
            normalized_current_change_today_high = row['current_change_today_high'] / std_1_month

            dollar_volume = row['dollar_volume']
            rsi_14_window = row['rsi_14_window']
            rsi_14_window_prev1 = row['rsi_14_window_prev1']
            # rsi_14_window_prev2 = row['rsi_14_window_prev2']
            normalized_pre_market_change = row['pre_market_change'] / std_1_month
            normalized_prev_window_change = row['prev_window_change'] / std_1_month
            true_range_1_month = row['true_range_1_month']
            current_volume_change = row['current_volume_change']
            # prev_volume_change = row['prev_volume_change']

            x = [side, entry_time, normalized_yesterday_change, normalized_change_5_day, normalized_change_1_month,
                 normalized_change_1_month_low, normalized_change_1_month_high,
                 normalized_current_change_today_low, normalized_current_change_today_high,
                 normalized_pre_market_change, dollar_volume, rsi_14_window, rsi_14_window_prev1,
                 normalized_prev_window_change, true_range_1_month, current_volume_change]
            feature.append(x)
        return np.array(feature)

    @staticmethod
    def _get_data(df: pd.DataFrame,
                  start_date: Optional[DATETIME_TYPE] = None,
                  end_date: Optional[DATETIME_TYPE] = None,
                  sort: bool = False):
        start_index, end_index = 0, len(df)
        for index, row in df.iterrows():
            if start_date is not None and pd.to_datetime(row['date']) < start_date:
                start_index = index + 1
            if end_date is not None and pd.to_datetime(row['date']) > end_date:
                end_index = index
                break
        sub_df = df.iloc[start_index:end_index]
        if sort:
            sub_df = sub_df.sort_values(['date', 'entry_time'])

        meta, label, weight, profit = [], [], [], []
        for _, row in sub_df.iterrows():
            p = row['profit']
            y = 1 if p > 0 else 0
            w = np.abs(p)
            label.append(y)
            weight.append(w)
            profit.append(p)
            meta.append((row['date'], row['symbol'], row['entry_time'], row['exit_time']))
        return VwapModel._get_feature(sub_df), np.array(label), np.array(weight), np.array(profit), meta

    @staticmethod
    def _create_model():
        hyper_parameters = {'max_depth': 5,
                            'min_samples_leaf': 1,
                            'n_jobs': -1,
                            'random_state': 0}
        return ensemble.RandomForestClassifier(**hyper_parameters)

    @staticmethod
    def _print_metrics(y: np.ndarray, y_pred: np.ndarray):
        confusion_matrix_main = metrics.confusion_matrix(y, y_pred, labels=[0, 1])
        confusion_table_main = [['', 'Predict Lose', 'Predict Win'],
                                ['True Lose', confusion_matrix_main[0][0], confusion_matrix_main[0][1]],
                                ['True Win', confusion_matrix_main[1][0], confusion_matrix_main[1][1]]]
        print(tabulate(confusion_table_main, tablefmt='grid'))

    def train(self,
              data_path: str,
              start_date: Optional[DATETIME_TYPE] = None,
              end_date: Optional[DATETIME_TYPE] = None):
        df = pd.read_csv(data_path)
        x, y, w, _, _ = self._get_data(df, start_date, end_date)
        self._model = self._create_model()
        self._model.fit(x, y, w)

    def evaluate(self,
                 data_path: str,
                 start_date: Optional[DATETIME_TYPE] = None,
                 end_date: Optional[DATETIME_TYPE] = None):
        df = pd.read_csv(data_path)
        x, y, _, profit, meta = self._get_data(df, start_date, end_date, sort=True)
        y_pred = self._model.predict(x)
        self._print_metrics(y, y_pred)
        asset = 1
        current_date = None
        current_time = None
        for y, p, meta in zip(y_pred, profit, meta):
            if y == 1:
                if current_date != meta[0]:
                    current_date = meta[0]
                    current_time = datetime.datetime.strptime(meta[3], '%H:%M:%S')
                else:
                    entry_time = datetime.datetime.strptime(meta[2], '%H:%M:%S')
                    if entry_time < current_time:
                        continue
                    else:
                        current_time = datetime.datetime.strptime(meta[3], '%H:%M:%S')
                asset *= 1 + p
        print(f'Gain/Loss: {(asset - 1) * 100:.2f}%')
        return asset - 1

    def save(self, model_path):
        with open(model_path, 'wb') as f:
            pickle.dump(self._model, f)

    def load(self, model_path):
        with open(model_path, 'rb') as f:
            self._model = pickle.load(f)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        x = self._get_feature(df)
        return self._model.predict(x)


def evaluate_model(data_path: str, save_model: bool = True):
    os.makedirs(MODEL_ROOT, exist_ok=True)
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    start_date = df.index[0] + relativedelta(months=3)
    start_date = pd.to_datetime(f'{start_date.year}-{start_date.month}-01')
    end_date = df.index[-1]
    current = start_date
    asset = 1
    t = [current]
    history = [asset]
    while current <= end_date:
        train_start = current - relativedelta(months=3)
        train_end = current - relativedelta(days=1)
        eval_start = current
        eval_end = current + relativedelta(months=1) - relativedelta(days=1)
        print(f'===[{eval_start} ~ {eval_end}]======')
        m = VwapModel()
        m.train(data_path, train_start, train_end)
        profit = m.evaluate(data_path, eval_start, eval_end)
        if save_model:
            m.save(os.path.join(MODEL_ROOT, eval_start.strftime('vwap-%Y-%m.pickle')))
        asset *= 1 + profit
        current += relativedelta(months=1)
        history.append(asset)
        t.append(current)
        print(f'Total Gain/Loss: {(asset - 1) * 100:.2f}%')
    text_kwargs = {'family': 'monospace'}
    plt.figure(figsize=(10, 4))
    plt.plot(t, history)
    plt.xlabel('Date', **text_kwargs)
    plt.ylabel('Normalized Value', **text_kwargs)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.tight_layout()
    plt.grid(linestyle='--', alpha=0.5)
    plt.show()
    plt.close()
