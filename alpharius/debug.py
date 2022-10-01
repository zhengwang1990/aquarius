from trade import *
import argparse
import datetime
import os
import mplfinance as fplt
import pandas as pd

CACHE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), '../cache')


def vwap(df):
    res = []
    vwaps = df['VWAP']
    volumes = df['Volume']
    total_dolloar = 0
    total_volume = 0
    for i in range(len(df)):
        total_dolloar += vwaps[i] * volumes[i]
        total_volume += volumes[i]
        res.append((df.index[i], total_dolloar / total_volume))
    return res


def plot(date, symbol):
    intraday_loader = DataLoader(TimeInterval.FIVE_MIN, DataSource.ALPACA)
    interday_loader = DataLoader(TimeInterval.DAY, DataSource.ALPACA)
    current_date = pd.to_datetime(date)
    intraday_data = intraday_loader.load_daily_data(symbol, current_date)
    interday_data = interday_loader.load_data_list(symbol,
                                                   current_date - datetime.timedelta(days=30),
                                                   current_date)
    fplt.plot(intraday_data, type='candle', style='charles', title=f'{symbol} on {date}', figsize=(20, 9),
              alines=vwap(intraday_data), volume=True)
    fplt.plot(interday_data, type='candle', style='charles', title=f'{symbol}', figsize=(20, 9))


def main():
    parser = argparse.ArgumentParser(description='Plot candles.')
    parser.add_argument('--date', default=None)
    parser.add_argument('--symbol', default=None)
    args = parser.parse_args()

    if args.date is None or args.symbol is None:
        raise ValueError('Flag date and symbol must be specified')

    plot(args.date, args.symbol)


if __name__ == '__main__':
    main()
