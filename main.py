from aquarius import *


def main():
    bt = Backtesting(start_date='2016-01-01', end_date='2021-07-31',
                     processor_factories=[SwingProcessorFactory(),
                                          LevelBreakoutProcessorFactory(),
                                          VolumeBreakoutProcessorFactory()])

    bt.run()


if __name__ == main():
    main()
