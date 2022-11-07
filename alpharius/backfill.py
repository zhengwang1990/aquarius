import argparse
import datetime

from db import Db


def main():
    parser = argparse.ArgumentParser(description='Alpharius backfill database.')
    parser.add_argument('--start_date', default=None,
                        help='Start date of the backfilling.')
    args = parser.parse_args()

    today = datetime.datetime.today().strftime('%F')
    client = Db()
    start_date = args.start_date or today
    client.backfill(start_date)


if __name__ == '__main__':
    main()
