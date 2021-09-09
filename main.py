from aquarius import *
import os


def main():
    bt = Backtesting(start_date='2016-01-01', end_date='2017-12-31',
                     processor_factories=[LevelBreakoutProcessorFactory()])

    bt.run()


if __name__ == main():
    main()
