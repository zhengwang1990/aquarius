from aquarius import *


def main():
    bt = Backtesting(start_date='2020-01-01', end_date='2021-07-28',
                     processor_factories=[VwapProcessorFactory()])

    bt.run()


if __name__ == main():
    main()

