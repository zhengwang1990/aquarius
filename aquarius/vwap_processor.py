from .common import *
from .model import Model
from .stock_universe import StockUniverse
from typing import List, Optional
import datetime
import numpy as np
import pandas as pd
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
        self._stock_unviverse = VwapStockUniverse(start_time=lookback_start_date,
                                                  end_time=lookback_end_date,
                                                  data_source=data_source)
        self._stock_unviverse.set_dollar_volume_filter(low=1E7)
        self._stock_unviverse.set_average_true_range_percent_filter(low=0.01)
        self._stock_unviverse.set_price_filer(low=1)
        self._hold_positions = {}
        self._feature_extractor = VwapFeatureExtractor()
        self._enable_model = enable_model
        self._models = {}

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return self._stock_unviverse.get_stock_universe(view_time)

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

    def _get_model(self, current_time: DATETIME_TYPE) -> Model:
        model_path = os.path.join(MODEL_ROOT, current_time.strftime('%Y-%m.pickle'))
        if model_path not in self._models:
            model = Model()
            model.load(model_path)
            self._models[model_path] = model
        return self._models[model_path]

    def teardown(self, output_dir: Optional[str] = None) -> None:
        if output_dir is not None:
            path = os.path.join(output_dir, 'vwap_data.csv')
            self._feature_extractor.save(path)


class VwapProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               *args, **kwargs) -> VwapProcessor:
        return VwapProcessor(lookback_start_date, lookback_end_date, data_source, enable_model=True)


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

    def extract_feature(self,
                        symbol: str,
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
        self._data.append(data)
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
        data = feature.iloc[0].values + [exit_time.strftime('%H:%M:%S'), profit]
        self._data.append(data)

    def save(self, data_path: Optional[str]) -> None:
        df = pd.DataFrame(self._data, columns=_FEATURES + _LABELS)
        df.to_csv(data_path, index=False)
