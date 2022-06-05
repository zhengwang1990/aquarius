from alpharius.common import *
from .dataset import Dataset
from .model import Model
import os


class Pipeline:

    def __init__(self, symbol, start_date, end_date):
        self._symbol = symbol
        self._start_date = start_date
        self._end_date = end_date
        self._model = Model()

    def run(self, train_only=False):
        data = Dataset()
        model_dir = os.path.join(MODEL_ROOT, self._symbol)
        os.makedirs(model_dir, exist_ok=True)
        if train_only:
            data_iterator = data.train_iterator(self._symbol, self._start_date, self._end_date)
        else:
            data_iterator = data.train_test_iterator(self._symbol, self._start_date, self._end_date)
        for ds in data_iterator:
            train_x, train_y = ds.train_data
            model_name = ds.name
            model_path = os.path.join(model_dir, model_name)
            self._model.log_title(f'{self._symbol} : {model_name}')
            if os.path.exists(model_path):
                self._model.load(model_path)
            else:
                self._model.train(train_x, train_y)
                self._model.save(model_path)
            if not train_only:
                test_x, test_y = ds.test_data
                self._model.evaluate(test_x, test_y, 0.5, -0.5)
        self._model.summarize()


def main():
    symbol = 'TSLA'
    start_date = '2021-01-01'
    end_date = '2022-06-01'
    pipeline = Pipeline(symbol, start_date, end_date)
    pipeline.run()
