from aquarius import *
import os


def main():
    # bt = Backtesting(start_date='2018-01-01', end_date='2021-07-31',
    #                  processor_factories=[VwapProcessorFactory(enable_model=True)])
    #
    # bt.run()

    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'outputs',
                             'backtesting',
                             '09-04',
                             '04',
                             'data.csv')
    vwap_evaluate_model(data_path)


if __name__ == main():
    main()
