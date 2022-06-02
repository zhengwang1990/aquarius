import dataset
import model
import os


_ML_ROOT = os.path.dirname(os.path.realpath(__file__))


class Pipeline:

    def __init__(self, symbol, start_date, end_date):
        self._symbol = symbol
        self._start_date = start_date
        self._end_date = end_date
        self._model = model.Model()

    def run(self):
        data = dataset.Dataset(self._symbol, self._start_date, self._end_date)
        model_dir = os.path.join(_ML_ROOT, 'models', self._symbol)
        os.makedirs(model_dir, exist_ok=True)
        tp, fp = 0, 0
        for ds in data.get_train_test():
            train_x, train_y = ds.train_data
            test_x, test_y = ds.test_data
            model_name = ds.name
            model_path = os.path.join(model_dir, model_name)
            if os.path.exists(model_path):
                self._model.load(model_path)
            else:
                self._model.train(train_x, train_y)
                self._model.save(model_path)
            self._model.print(f'--[{self._symbol} : {model_name}]' + '-' * 60)
            confusion_matrix = self._model.evaluate(test_x, test_y, 0.5, -0.5)
            tp += confusion_matrix[2][2]
            fp += confusion_matrix[0][2]
        self._model.print(f'Estimated success rate: {tp / (tp + fp + 1E-7) : .4f} ({tp} / {tp + fp})')


def main():
    symbol = 'TQQQ'
    start_date = '2020-01-01'
    end_date = '2022-06-01'
    pipeline = Pipeline(symbol, start_date, end_date)
    pipeline.run()


if __name__ == '__main__':
    main()
