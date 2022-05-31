from .common import *
from tensorflow import keras
from typing import List
import datetime
import numpy as np
import os

_MARKET_START = datetime.time(9, 30)
_COLLECT_START = datetime.time(10, 0)
_COLLECT_END = datetime.time(15, 0)


class MlProcessor(Processor):

    def __init__(self,
                 output_dir: str) -> None:
        super().__init__()
        self._open_positions = set()
        self._models = dict()
        self._output_dir = output_dir
        self._logger = logging_config(os.path.join(self._output_dir, 'ml_processor.txt'),
                                      detail=True,
                                      name='ml_processor')

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['TSLA']

    def setup(self, hold_positions: List[Position]) -> None:
        model_names = os.listdir(MODEL_ROOT)
        for name in model_names:
            if name in self._models:
                continue
            model_path = os.path.join(MODEL_ROOT, name)
            model = keras.models.load_model(model_path)
            self._models[name] = model

    def process_data(self, context: Context) -> Optional[Action]:
        if context.current_time.time() < _COLLECT_START:
            return
        if context.symbol in self._open_positions:
            return self._close_position(context)
        if context.current_time.time() < _COLLECT_END:
            return self._open_position(context)

    def _get_prediction(self, context: Context) -> Optional[float]:
        model_name = f'{context.current_time.strftime("%Y-%m")}-{context.symbol}'
        model = self._models[model_name]
        interday_open = context.interday_lookback['Open']
        interday_close = context.interday_lookback['Close']
        interday_input = []
        for i in range(-240, 0):
            t_feature = np.array([(interday_close[i] / interday_open[i] - 1) * 100,
                                  (interday_close[i] / interday_close[i - 1] - 1) * 100,
                                  (interday_open[i] / interday_close[i - 1] - 1) * 100])
            interday_input.append(t_feature)
        intraday_start = pd.to_datetime(
            pd.Timestamp.combine(context.current_time.date(), _MARKET_START)).tz_localize(TIME_ZONE)
        market_start_index = timestamp_to_index(context.intraday_lookback.index, intraday_start)
        if market_start_index is None:
            return 0
        intraday_input = []
        intraday_close = context.intraday_lookback['Close']
        intraday_open = context.intraday_lookback['Open']
        end_index = len(context.intraday_lookback)
        for j in range(end_index - 66, end_index):
            if j >= market_start_index:
                t_feature = np.array([(intraday_close[j] / intraday_open[j] - 1) * 100,
                                      (intraday_close[j] / interday_close[-1] - 1) * 100])
            else:
                t_feature = np.array([0, 0, 0])
            intraday_input.append(t_feature)
        interday_input = np.array(interday_input)
        intraday_input = np.array(intraday_input)
        label = model.predict([np.array([interday_input]), np.array([intraday_input])])[0]
        return label

    def _open_position(self, context: Context) -> Optional[Action]:
        label = self._get_prediction(context)
        if label > 0.75:
            self._open_positions.add(context.symbol)
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        label = self._get_prediction(context)
        if label < 0 or context.current_time.time() == datetime.time(16, 0):
            self._open_positions.remove(context.symbol)
            return Action(context.symbol, ActionType.SELL_TO_CLOSE, 1, context.current_price)


class MlProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               lookback_start_date: DATETIME_TYPE,
               lookback_end_date: DATETIME_TYPE,
               data_source: DataSource,
               output_dir: str,
               *args, **kwargs) -> MlProcessor:
        return MlProcessor(output_dir)
