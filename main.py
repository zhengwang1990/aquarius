from aquarius import *
import os


def main():
    bt = Backtesting(start_date='2015-10-01', end_date='2017-12-31',
                     processor_factories=[KeyLevelProcessorFactory()])

    bt.run()

    # data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    #                          'outputs',
    #                          'backtesting',
    #                          '09-06',
    #                          '02',
    #                          'vwap_data.csv')
    # vwap_evaluate_model(data_path)


if __name__ == main():
    main()
