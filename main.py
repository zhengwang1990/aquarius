import pandas as pd

from aquarius import *
import os

def main():
    #bt = Backtesting(start_date='2020-01-01', end_date='2021-07-28',
    #                 processor_factories=[VwapProcessorFactory()])

    #bt.run()
    m = Model()
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'outputs',
                             'backtesting',
                             '08-21',
                             '07',
                             'data.csv')
    m.train(data_path, pd.to_datetime('2020-07-01'), pd.to_datetime('2020-09-30'))
    m.evaluate(data_path, pd.to_datetime('2020-10-01'), pd.to_datetime('2020-10-31'))


if __name__ == main():
    main()
