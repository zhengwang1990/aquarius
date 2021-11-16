import argparse
import alpharius
import datetime
import pandas_market_calendars as mcal


def main():
    parser = argparse.ArgumentParser(description='Alpharius stock trading.')

    parser.add_argument('-m', '--mode', help='Running mode. Can be backtest or trade.',
                        required=True, choices=['backtest', 'trade'])
    parser.add_argument('--start_date', default=None,
                        help='Start date of the backtesting. Only used in backtest mode.')
    parser.add_argument('--end_date', default=None,
                        help='End date of the backtesting. Only used in backtest mode.')
    args = parser.parse_args()

    processor_factories = [
        alpharius.BestMetricProcessorFactory(),
    ]
    today = datetime.datetime.today()
    if args.mode == 'backtest':
        default_start_date = today - datetime.timedelta(days=252)
        default_end_date = today + datetime.timedelta(days=1)
        start_date = args.start_date or default_start_date.strftime('%F')
        end_date = args.end_date or default_end_date.strftime('%F')
        backtesting = alpharius.Backtesting(start_date=start_date, end_date=end_date,
                                            processor_factories=processor_factories)
        backtesting.run()
    else:
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=today,
                                 end_date=today)
        if len(schedule) == 0:
            print(f'Market not open on [{today.strftime("%F")}]')
            return
        trading = alpharius.Trading(processor_factories=processor_factories)
        trading.run()


if __name__ == main():
    main()
