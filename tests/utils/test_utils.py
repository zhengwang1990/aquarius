import datetime

import pandas as pd
from alpharius.utils import get_transactions
from tests.fakes import Order


def test_get_transactions(mocker, mock_alpaca):
    orders = []
    for i in range(400):
        orders.append(Order(
            f'id{2 * i}', 'SYM', 'sell', '14', None, '10',
            pd.to_datetime('2021-03-17T10:14:57.0Z') - datetime.timedelta(seconds=2 * i), '12',
            pd.to_datetime('2021-03-17T10:14:57.0Z') - datetime.timedelta(seconds=2 * i)))
        orders.append(Order(
            f'id{2 * i + 1}', 'SYM', 'buy', '14', None, '10',
            pd.to_datetime('2021-03-17T10:14:57.0Z') - datetime.timedelta(seconds=2 * i + 1), '11.99',
            pd.to_datetime('2021-03-17T10:14:57.0Z') - datetime.timedelta(seconds=2 * i + 1)))
    list_orders = mocker.patch.object(mock_alpaca, 'list_orders', side_effect=[orders[:500], orders[497:]])

    transactions = get_transactions('2021-03-17')

    assert list_orders.call_count == 2
    assert len(transactions) == 400
