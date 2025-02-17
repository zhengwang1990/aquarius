import argparse
import datetime

import matplotlib
from dateutil.relativedelta import relativedelta

from alpharius.data import get_default_data_client
from alpharius.trade import Backtest, Live, processors
from alpharius.utils import get_latest_day

# Interactive plot is not disabled when trading or backtesting is invoked.
matplotlib.use('agg')

PROCESSOR_FACTORIES = [
    # processors.AbcdProcessorFactory(),
    # processors.BearMomentumProcessorFactory(),
    # processors.CrossCloseProcessorFactory(),
    # processors.DownFourProcessorFactory(),
    # processors.FirstHourM6mProcessorFactory(),
    # processors.H2lFiveMinProcessorFactory(),
    # processors.H2lHourProcessorFactory(),
    # processors.L2hProcessorFactory(),
    # processors.O2hProcessorFactory(),
    # processors.O2lProcessorFactory(),
    # processors.OpenHighProcessorFactory(),
    # processors.OvernightProcessorFactory(),
    # processors.TqqqProcessorFactory(),
    processors.DataCollectProcessorFactory(),
]


def main():
    parser = argparse.ArgumentParser(description='Alpharius stock trading.')

    parser.add_argument('-m', '--mode', help='Running mode. Can be backtest or trade.',
                        required=True, choices=['backtest', 'live'])
    parser.add_argument('--start_date', default=None,
                        help='Start date of the backtesting. Only used in backtest mode.')
    parser.add_argument('--end_date', default=None,
                        help='End date of the backtesting. Only used in backtest mode.')
    parser.add_argument('--ack_all', action='store_true',
                        help='Ack all trade actions. Only used in backtest mode.')
    args = parser.parse_args()
    data_client = get_default_data_client()

    if args.mode == 'backtest':
        latest_day = get_latest_day()
        default_start_date = (latest_day - relativedelta(years=1)).strftime('%F')
        default_end_date = (latest_day + datetime.timedelta(days=1)).strftime('%F')
        start_date = args.start_date or default_start_date
        end_date = args.end_date or default_end_date
        runner = Backtest(start_date=start_date, end_date=end_date,
                          processor_factories=PROCESSOR_FACTORIES,
                          data_client=data_client,
                          ack_all=args.ack_all)
        runner.run()
    else:
        runner = Live(processor_factories=PROCESSOR_FACTORIES,
                      data_client=data_client)
        runner.run()


if __name__ == '__main__':
    main()
