import argparse
import datetime

import matplotlib
from dateutil.relativedelta import relativedelta
from alpharius.trade import Backtesting, Trading, processors
from alpharius.utils import get_latest_day

# Interactive plot is not disabled when trading or backtesting is invoked.
matplotlib.use('agg')

PROCESSOR_FACTORIES = [
    processors.OvernightProcessorFactory(),
    processors.ZScoreProcessorFactory(),
    processors.O2lProcessorFactory(),
    processors.O2hProcessorFactory(),
    processors.BearMomentumProcessorFactory(),
    processors.H2lOneHourProcessorFactory(),
    processors.H2lFiveMinProcessorFactory(),
]


def main():
    parser = argparse.ArgumentParser(description='Alpharius stock trading.')

    parser.add_argument('-m', '--mode', help='Running mode. Can be backtest or trade.',
                        required=True, choices=['backtest', 'trade'])
    parser.add_argument('--start_date', default=None,
                        help='Start date of the backtesting. Only used in backtest mode.')
    parser.add_argument('--end_date', default=None,
                        help='End date of the backtesting. Only used in backtest mode.')
    args = parser.parse_args()

    if args.mode == 'backtest':
        latest_day = get_latest_day()
        default_start_date = (latest_day - relativedelta(years=1)).strftime('%F')
        default_end_date = (latest_day + datetime.timedelta(days=1)).strftime('%F')
        start_date = args.start_date or default_start_date
        end_date = args.end_date or default_end_date
        runner = Backtesting(start_date=start_date, end_date=end_date,
                             processor_factories=PROCESSOR_FACTORIES)
        runner.run()
    else:
        runner = Trading(processor_factories=PROCESSOR_FACTORIES)
        runner.run()


if __name__ == '__main__':
    main()
