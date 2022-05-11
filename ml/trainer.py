import os
import pandas as pd

_ML_ROOT = os.path.dirname(os.path.realpath(__file__))


def _get_d1_d2(prefix, columns):
    d1 = 1
    d2 = 1
    while f'{prefix}_{d1}_{d2}' in columns:
        d2 += 1
    d2 -= 1
    while f'{prefix}_{d1}_{d2}' in columns:
        d1 += 1
    d1 -= 1
    return d1, d2


def _get_row(prefix, d1, d2, data_row):
    row = []
    for f1 in range(1, d1 + 1):
        pt = []
        for f2 in range(1, d2 + 1):
            feature_name = f'{prefix}_{f1}_{f2}'
            pt.append(data_row[feature_name] * 100)
        row.append(pt)
    return row


class Trainer:

    def __init__(self, data_input: str):
        self._data = pd.read_csv(data_input)
        curr_month = self._data['date'].iloc[0][:7]
        self._months = [(curr_month, 0)]
        for i, d in enumerate(self._data['date']):
            if d[:7] != curr_month:
                curr_month = d[:7]
                self._months.append((curr_month, i))
        self._months.append(('', len(self._data['date'])))
        columns = set(self._data.columns)
        self._inter_d1, self._inter_d2 = _get_d1_d2('inter', columns)
        self._intra_d1, self._intra_d2 = _get_d1_d2('intra', columns)

    def prepare_data(self, start_month_idx: int, end_month_idx: int):
        start_data_idx = self._months[start_month_idx][1]
        end_data_idx = self._months[end_month_idx][1]
        inter_data = []
        intra_data = []
        labels = []
        for i in range(start_data_idx, end_data_idx):
            data_row = self._data.iloc[i]
            inter_row = _get_row('inter', self._inter_d1, self._inter_d2, data_row)
            intra_row = _get_row('intra', self._intra_d1, self._intra_d2, data_row)
            label = data_row['label']
            if label > 1E-3:
                label = 1
            elif label < -1E-3:
                label = -1
            else:
                label = 0
            inter_data.append(inter_row)
            intra_data.append(intra_row)
            labels.append(label)
        return [inter_data, intra_data], labels


def main():
    data_input = os.path.join(_ML_ROOT, 'data', 'TQQQ_2020-01-01_2021-01-01.csv')
    trainer = Trainer(data_input)
    data = trainer.prepare_data(0, 1)


if __name__ == '__main__':
    main()
