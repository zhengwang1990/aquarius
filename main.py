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
    m.train(data_path)


if __name__ == main():
    main()
