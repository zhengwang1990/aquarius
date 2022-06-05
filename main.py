from alpharius import ml
from alpharius import processors
from dateutil import relativedelta
import argparse
import alpharius
import datetime
import pandas_market_calendars as mcal


def main():
    parser = argparse.ArgumentParser(description='Alpharius stock trading.')

    parser.add_argument('-m', '--mode', help='Running mode. Can be backtest, trade or ml.',
                        required=True, choices=['backtest', 'trade', 'ml'])
    parser.add_argument('--start_date', default=None,
                        help='Start date of the backtesting. Only used in backtest & ml mode.')
    parser.add_argument('--end_date', default=None,
                        help='End date of the backtesting. Only used in backtest & ml mode.')
    parser.add_argument('--symbol', default=None,
                        help='Stock symbol for ML evaluation. Only used in ml mode.')
    parser.add_argument('--train_only', action='store_true',
                        help='Run ML model training without testing. Only used in ml mode')
    args = parser.parse_args()

    processor_factories = [
        # processors.MlProcessorFactory(),
        processors.OvernightProcessorFactory(),
        # processors.IntradayReversalProcessorFactory(),
        # processors.IntradayMomentumProcessorFactory(),
    ]
    today = datetime.datetime.today()
    if args.mode == 'backtest':
        default_start_date = (today - relativedelta.relativedelta(years=1)).strftime('%F')
        default_end_date = (today + datetime.timedelta(days=1)).strftime('%F')
        start_date = args.start_date or default_start_date
        end_date = args.end_date or default_end_date
        backtesting = alpharius.Backtesting(start_date=start_date, end_date=end_date,
                                            processor_factories=processor_factories)
        backtesting.run()
    elif args.mode == 'trade':
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=today,
                                 end_date=today)
        if len(schedule) == 0:
            print(f'Market not open on [{today.strftime("%F")}]')
            return
        trading = alpharius.Trading(processor_factories=processor_factories)
        trading.run()
    else:
        default_start_date = (today - relativedelta.relativedelta(years=1)).strftime('%Y-%m-01')
        default_end_date = today.strftime('%Y-%m-01')
        start_date = args.start_date or default_start_date
        end_date = args.end_date or default_end_date
        if not args.symbol:
            raise ValueError('Symbol must be provided in ML mode')
        pipeline = ml.Pipeline(args.symbol, start_date, end_date)
        pipeline.run(args.train_only)


if __name__ == '__main__':
    main()
