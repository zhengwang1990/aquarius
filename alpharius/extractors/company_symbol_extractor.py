"""
Extracts all stock symbols in the US stock market.
1. First go to https://www.nasdaq.com/market-activity/stocks/screener and download csv
2. Run this script to extract the stock symbols
"""
import argparse
import pandas as pd
import pathlib
import os
import re
import textwrap


def main():
    parser = argparse.ArgumentParser(description='Stock symbol extractor.')

    parser.add_argument('--input_path', default=None,
                        help='provide input file path.')
    args = parser.parse_args()
    input_path = args.input_path
    if not input_path:
        download_dir = os.path.join(pathlib.Path.home(), 'Downloads')
        files = os.listdir(download_dir) if os.path.exists(download_dir) else []
        for file in files:
            if file.startswith('nasdaq_screener') and file.endswith('.csv'):
                input_path = os.path.join(download_dir, file)
                break
        else:
            raise ValueError('Input file not found')
    df = pd.read_csv(input_path)
    symbols = [f"'{symbol}'" for symbol in df['Symbol'] if re.match('^[A-Z]*$', symbol)]
    symbols_line = ', '.join(symbols)
    lines = textwrap.wrap(symbols_line, width=80)
    print('COMPANY_SYMBOLS = [')
    print('\n'.join(['    ' + line for line in lines]))
    print(']')


if __name__ == '__main__':
    main()
