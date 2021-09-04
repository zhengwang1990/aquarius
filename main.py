from aquarius import *
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
import matplotlib.pyplot as plt

MODEL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'models')


def main():
    bt = Backtesting(start_date='2018-01-01', end_date='2021-07-31',
                     processor_factories=[VwapProcessorFactory()])

    bt.run()

    # os.makedirs(MODEL_DIR, exist_ok=True)
    # m = Model()
    # data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    #                          'outputs',
    #                          'backtesting',
    #                          '09-02',
    #                          '01',
    #                          'data.csv')
    # df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    # start_date = df.index[0] + relativedelta(months=3)
    # start_date = pd.to_datetime(f'{start_date.year}-{start_date.month}-01')
    # end_date = df.index[-1]
    # current = start_date
    # asset = 1
    # t = [current]
    # history = [asset]
    # while current <= end_date:
    #     train_start = current - relativedelta(months=3)
    #     train_end = current - relativedelta(days=1)
    #     eval_start = current
    #     eval_end = current + relativedelta(months=1) - relativedelta(days=1)
    #     print(f'===[{eval_start} ~ {eval_end}]======')
    #     m.train(data_path, train_start, train_end)
    #     profit = m.evaluate(data_path, eval_start, eval_end)
    #     m.save(os.path.join(MODEL_DIR, eval_start.strftime('%Y-%m.pickle')))
    #     asset *= 1 + profit
    #     current += relativedelta(months=1)
    #     history.append(asset)
    #     t.append(current)
    # print(f'Total Gain/Loss: {(asset - 1) * 100:.2f}%')
    # plt.plot(t, history)
    # plt.grid(linestyle='--', alpha=0.5)
    # plt.show()


if __name__ == main():
    main()
