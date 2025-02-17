import sqlite3
import os
import pandas as pd
import tqdm

from alpharius.trade.common import CACHE_DIR


COLUMNS = ['symbol', 'entry_time', 'current_bar_loss', 'prev_bar_loss', 'h2l_avg', 'entry_price', 'exit_price_5min',
           'exit_price_10min', 'exit_price_15min', 'exit_price_20min']
READ_SCRIPT = f'SELECT {", ".join(COLUMNS)} FROM data'


def filter(df):
    return df

def search1(df):
    n_step = 15
    min_count = 4000
    ch_upper = max(df['ch'])
    ch_step = (ch_upper - min(df['ch'])) / n_step
    print('ch range', min(df['ch']), max(df['ch']))
    ph_lower = min(df['ph'])
    ph_step = (max(df['ph']) - ph_lower) / n_step
    print('ph range', min(df['ph']), max(df['ph']))
    h2l_upper = max(df['h2l_avg'])
    h2l_step = (h2l_upper - min(df['h2l_avg'])) / n_step
    print('h2l range', min(df['h2l_avg']), max(df['h2l_avg']))
    df1 = df
    max_total_gl = 0
    max_rate = 0
    max_gl = 0
    for i in range(n_step):
        print('i', i)
        df = df1
        ch = ch_upper - i * ch_step
        df = df[df['ch'] > ch]
        if len(df) < min_count:
            continue
        df2 = df
        for j in range(n_step):
            df = df2
            ph = ph_lower + j * ph_step
            df = df[df['ph'] < ph]
            if len(df) < min_count:
                continue
            df3 = df
            for k in range(n_step):
                df = df3
                h2l = h2l_upper - k * h2l_step
                df = df[df['h2l_avg'] < h2l]
                if len(df) < min_count:
                    continue
                df33 = df
                for kk in range(k + 1, n_step + 1):
                    df = df33
                    h2l2 = h2l_upper - kk * h2l_step
                    df = df[df['h2l_avg'] > h2l2]
                    total = len(df)
                    if total < min_count:
                        continue
                    win = len(df[df['gl'] > 0])
                    win_rate = win / total
                    balance = 1
                    for gl in df['gl']:
                        balance = balance * (1 + gl - 0.0015)
                    total_gl = balance - 1
                    gl = balance ** (1 / total) - 1
                    if win_rate > max_rate or gl > max_gl or total_gl > max_total_gl:
                        print('ch>', ch, 'ph<', ph, 'h2l', h2l2, '~', h2l, 'total', total, 'win rate', win_rate, 'total_gl', total_gl, 'avg gl', gl)
                        max_gl = max(gl, max_gl)
                        max_rate = max(win_rate, max_rate)
                        max_total_gl = max(total_gl, max_total_gl)

def search(df):
    n_step = 20
    min_count = 4000
    ch_upper = max(df['ch'])
    ch_step = (ch_upper - min(df['ch'])) / n_step
    print('ch range', min(df['ch']), max(df['ch']))
    ph_lower = min(df['ph'])
    ph_step = (max(df['ph']) - ph_lower) / n_step
    print('ph range', min(df['ph']), max(df['ph']))
    h2l_upper = max(df['h2l_avg'])
    h2l_step = (h2l_upper - min(df['h2l_avg'])) / n_step
    print('h2l range', min(df['h2l_avg']), max(df['h2l_avg']))
    df1 = df
    max_total_gl = 0
    max_rate = 0
    max_gl = 0
    for i in range(n_step):
        print(f'{i} / {n_step}')
        df = df1
        ch = ch_upper - i * ch_step
        df = df[df['ch'] < ch]
        if len(df) < min_count:
            continue
        df11 = df
        for ii in range(i + 1, n_step + 1):
            ch2 = ch_upper - ii * ch_step
            df = df11
            df = df[df['ch'] > ch2]
            if len(df) < min_count:
                continue
            df2 = df
            for j in range(n_step):
                df = df2
                ph = ph_lower + j * ph_step
                df = df[df['ph'] > ph]
                if len(df) < min_count:
                    continue
                df22 = df
                for jj in range(j + 1, n_step + 1):
                    df = df22
                    ph2 = ph_lower + jj * ph_step
                    df = df[df['ph'] < ph2]
                    if len(df) < min_count:
                        continue
                    df3 = df
                    for k in range(n_step):
                        df = df3
                        h2l = h2l_upper - k * h2l_step
                        df = df[df['h2l_avg'] < h2l]
                        if len(df) < min_count:
                            continue
                        df33 = df
                        for kk in range(k + 1, n_step + 1):
                            df = df33
                            h2l2 = h2l_upper - kk * h2l_step
                            df = df[df['h2l_avg'] > h2l2]
                            total = len(df)
                            if total < min_count:
                                continue
                            win = len(df[df['gl'] > 0])
                            win_rate = win / total
                            balance = 1
                            for gl in df['gl']:
                                balance = balance * (1 + gl - 0.0015)
                            total_gl = balance - 1
                            gl = balance ** (1 / total) - 1
                            if win_rate > max_rate or gl > max_gl or total_gl > max_total_gl:
                                print('ch', ch2, '~', ch, 'ph', ph, '~', ph2, 'h2l', h2l2, '~', h2l, 'total', total, 'win rate', win_rate, 'total_gl', total_gl, 'avg gl', gl)
                                max_gl = max(gl, max_gl)
                                max_rate = max(win_rate, max_rate)
                                max_total_gl = max(total_gl, max_total_gl)


def main():
    data_dir = os.path.join(CACHE_DIR, 'down_four_data')
    files = os.listdir(data_dir)
    df = pd.DataFrame([], columns=COLUMNS)
    for file in files[:-1]:
        data_file = os.path.join(data_dir, file, 'data_collect.db')
        conn = sqlite3.connect(data_file)
        res = conn.execute(READ_SCRIPT)
        data = res.fetchall()
        conn.close()
        df = pd.concat([df, pd.DataFrame(data, columns=COLUMNS)])
    df.reset_index(drop=True, inplace=True)
    print(df.columns)
    df['gl'] = df.apply(lambda row: row.exit_price_20min / row.entry_price - 1, axis=1)
    df['ch'] = df.apply(lambda row: row.current_bar_loss / row.h2l_avg, axis=1)
    df['ph'] = df.apply(lambda row: row.prev_bar_loss / row.h2l_avg, axis=1)
    df = df.drop(['current_bar_loss', 'prev_bar_loss', 'entry_price', 'exit_price_5min',
                  'exit_price_10min', 'exit_price_15min'], axis=1)
    print(f'Checking {len(df)} records')
    search(df)


if __name__ == '__main__':
    main()
