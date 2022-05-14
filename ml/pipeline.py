import dataset
import model


class Pipeline:

    def __init__(self, symbol, start_date, end_date):
        self._symbol = symbol
        self._start_date = start_date
        self._end_date = end_date

    def run(self):
        data_file = '_'.join([self._symbol, self._start_date, self._end_date]) + '.csv'
        data = dataset.Dataset()


def main():

    symbol = 'TQQQ'
    start_date = '2020-01-01'
    end_date = '2021-01-01'
    pipeline = Pipeline(symbol, start_date, end_date)
    pipeline.run()


if __name__ == '__main__':
    main()
