from aquarius import *
from dateutil.relativedelta import relativedelta
import pandas as pd
import os

def main():
    # bt = Backtesting(start_date='2019-10-01', end_date='2019-10-03',
    #                  processor_factories=[VwapProcessorFactory()])
    #
    # bt.run()

    m = Model()
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'outputs',
                             'backtesting',
                             '08-28',
                             '14',
                             'data.csv')
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    start_date = df.index[0] + relativedelta(months=3)
    start_date = pd.to_datetime(f'{start_date.year}-{start_date.month}-01')
    end_date = df.index[-1]
    current = start_date
    asset = 1
    while current <= end_date:
        train_start = current - relativedelta(months=3)
        train_end = current - relativedelta(days=1)
        eval_start = current
        eval_end = current + relativedelta(months=1) - relativedelta(days=1)
        print(f'===[{eval_start} ~ {eval_end}]======')
        m.train(data_path, train_start, train_end)
        profit = m.evaluate(data_path, eval_start, eval_end)
        asset *= 1 + profit
        current += relativedelta(months=1)
    print(f'Total Gain/Loss: {(asset - 1) * 100:.2f}%')


if __name__ == main():
    main()
