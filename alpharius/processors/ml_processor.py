from alpharius.common import *
from alpharius.ml.dataset import Dataset
from tensorflow import keras
from typing import List, Optional
import datetime
import numpy as np
import os

_MARKET_START = datetime.time(9, 30)
_COLLECT_START = datetime.time(10, 0)
_COLLECT_END = datetime.time(15, 0)
_STOCK_UNIVERSE = ['TSLA']


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
        self._current_month = None
        self._dataset = Dataset()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return _STOCK_UNIVERSE

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        current_month = current_time.strftime('%Y-%m')
        if self._current_month == current_month:
            return
        self._current_month = current_month
        for symbol in _STOCK_UNIVERSE:
            model_path = os.path.join(MODEL_ROOT, symbol, current_month)
            model = keras.models.load_model(model_path)
            self._models[symbol] = model

    def process_data(self, context: Context) -> Optional[Action]:
        if context.current_time.time() < _COLLECT_START:
            return
        if context.symbol in self._open_positions:
            return self._close_position(context)
        if context.current_time.time() < _COLLECT_END:
            return self._open_position(context)

    def _get_prediction(self, context: Context) -> Optional[float]:
        model = self._models[context.symbol]
        interday_input = self._dataset.get_interday_input(context.interday_lookback)
        intraday_input = self._dataset.get_intraday_input(context.intraday_lookback, context.prev_day_close)
        label = model.predict([np.array([interday_input]), np.array([intraday_input])])[0]
        return label

    def _open_position(self, context: Context) -> Optional[Action]:
        label = self._get_prediction(context)
        if label > 0.5:
            self._open_positions.add(context.symbol)
            return Action(context.symbol, ActionType.BUY_TO_OPEN, 1, context.current_price)

    def _close_position(self, context: Context) -> Optional[Action]:
        label = self._get_prediction(context)
        if label < 0.25 or context.current_time.time() == datetime.time(16, 0):
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
