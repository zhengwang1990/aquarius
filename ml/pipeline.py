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
        for ds in data.get_train_test():
            train_x, train_y = ds.train_data
            test_x, test_y = ds.test_data
            model_name = f'{ds.name}'
            if os.path.exists(os.path.join(_ML_ROOT, 'models', model_name)):
                self._model.load(model_name)
            else:
                self._model.train(train_x, train_y)
                self._model.save(model_name)
            self._model.print(f'--[{model_name}]' + '-' * 60)
            self._model.evaluate(test_x, test_y, 0.75, -0.75)


def main():
    symbol = 'TQQQ'
    start_date = '2020-01-01'
    end_date = '2022-01-01'
    pipeline = Pipeline(symbol, start_date, end_date)
    pipeline.run()


if __name__ == '__main__':
    main()
