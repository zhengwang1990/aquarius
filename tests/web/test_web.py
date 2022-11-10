import textwrap

import pandas as pd


def test_dashboard(client, mock_alpaca):
    assert client.get('/').status_code == 200
    assert mock_alpaca.get_portfolio_history_call_count > 0
    assert mock_alpaca.list_orders_call_count > 0
    assert mock_alpaca.list_positions_call_count > 0


def test_transactions(client, mock_engine):
    mock_engine.conn.execute.side_effect = [
        iter([[2]]),
        [
            ('SYMA', True, 'Processor', 11.1, 12.3,
             pd.to_datetime('2022-11-03T09:35:00-04:00'),
             pd.to_datetime('2022-11-03T10:35:00-04:00'),
             10, 100, 0.01, -100, -0.01),
            ('SYMB', False, 'Processor', 11.1, 12.3,
             pd.to_datetime('2022-11-03T09:35:00-04:00'),
             pd.to_datetime('2022-11-03T10:35:00-04:00'),
             10, 100, 0.01, None, None),
        ],
    ]

    assert client.get('/transactions').status_code == 200
    assert mock_engine.conn.execute.call_count == 2


def test_analytics(client, mock_engine):
    mock_engine.conn.execute.return_value = [
        (pd.to_datetime('2022-11-02').date(), 'Processor1',
         100, 0.01, 0, 0, 3, 2, 1, 0),
        (pd.to_datetime('2022-11-03').date(), 'Processor2',
         100, 0.01, -10, -0.01, 3, 2, 1, 1)]

    assert client.get('/analytics').status_code == 200
    assert mock_engine.conn.execute.call_count == 1


def test_logs(client, mock_engine):
    fake_data = textwrap.dedent("""
    [DEBUG] [2022-11-03 10:33:00] [main.py:11] This is debug log.
    [INFO] [2022-11-03 10:34:00] [main.py:12] This is info log.
    [WARNING] [2022-11-03 10:35:00] [main.py:13] This is warning log.
    [ERROR] [2022-11-03 10:36:00] [main.py:14] This is error log.
    More error messages.
    """)
    mock_engine.conn.execute.side_effect = [
        [[pd.to_datetime('2022-11-03').date()],
         [pd.to_datetime('2022-11-03').date()],
         [pd.to_datetime('2022-11-03').date()],
         [pd.to_datetime('2022-11-03').date()]],
        [['Trading', fake_data],
         ['Processor1', fake_data],
         ['Processor2', fake_data]],
    ]

    assert client.get('/logs').status_code == 200


def test_job_status(client):
    assert client.get('/job_status').status_code == 200
