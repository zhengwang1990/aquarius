import pandas as pd

from alpharius.db import Transaction

TEST_TRANSACTION = Transaction('SYMB', True, 'Processor', 10, 12,
                               pd.to_datetime('2022-11-03T16:00:00'),
                               pd.to_datetime('2022-11-04T09:35:00'),
                               100, 11, 0.2, -11, -0.01)


def test_insert_transaction(client, mock_engine):
    client.insert_transaction(TEST_TRANSACTION)

    mock_engine.conn.execute.assert_called_once()


def test_upsert_transaction(client, mock_engine):
    client.upsert_transaction(TEST_TRANSACTION)

    mock_engine.conn.execute.assert_called_once()


def test_update_aggregation(client, mock_engine):
    mock_engine.conn.execute.return_value = [
        ('id1', 'Processor1', 1, 0.01, None, None),
        ('id2', 'Processor1', 2, 0.02, -1, -0.01),
        ('id3', 'Processor2', -3, -0.03, 1, 0.01),
        ('id4', None, 2, 0.02, -1, -0.01),
    ]

    client.update_aggregation('2022-11-03')

    assert mock_engine.conn.execute.call_count == 3


def test_backfill(client, mock_engine):
    client.backfill('2022-11-03')

    assert mock_engine.conn.execute.call_count > 0
