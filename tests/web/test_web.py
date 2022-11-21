import textwrap

import pandas as pd
from alpharius.web import web


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


def test_analytics(client, mock_alpaca, mock_engine):
    mock_engine.conn.execute.return_value = [
        (pd.to_datetime('2022-11-02').date(), 'Processor1',
         100, 0.01, 0, 0, 3, 2, 1, 0),
        (pd.to_datetime('2022-11-03').date(), 'Processor1',
         100, 0.01, 10, 0.01, 2, 2, 0, 2),
        (pd.to_datetime('2022-11-03').date(), 'Processor2',
         100, 0.01, -10, -0.01, 3, 2, 1, 1)]

    assert client.get('/analytics').status_code == 200
    assert mock_engine.conn.execute.call_count == 1
    assert mock_alpaca.get_portfolio_history_call_count == 1
    assert mock_alpaca.get_bars_call_count > 0


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


def test_get_annual_return():
    dates = [pd.to_datetime(t, utc=True, unit='s').strftime('%F')
             for t in range(int(pd.to_datetime('2017-01-01', utc=True).timestamp()),
                            int(pd.to_datetime('2022-10-01', utc=True).timestamp()),
                            86400)]
    daily_prices = {'dates': dates,
                    'symbols': ['My Portfolio', 'SPY', 'QQQ'],
                    'values': [[100] * len(dates)] * 3}

    annual_return = web._get_annual_return(daily_prices)

    assert len(annual_return['returns'][0]) == 6


def test_get_risks():
    dates = [pd.to_datetime(t, utc=True, unit='s').strftime('%F')
             for t in range(int(pd.to_datetime('2017-01-01', utc=True).timestamp()),
                            int(pd.to_datetime('2022-01-01', utc=True).timestamp()) + 1,
                            86400)]
    daily_prices = {'dates': dates,
                    'symbols': ['My Portfolio', 'SPY', 'QQQ'],
                    'values': [[100 + i * 0.01 for i in range(len(dates))]] * 3}
    risks = web._get_risks(daily_prices)

    print(risks)

    assert len(risks) == 6  # only show last 5 years + ALL


def test_experiments(client):
    assert client.get('/experiments').status_code == 200


def test_charts(client, mock_alpaca):
    assert client.get('/charts?date=2022-11-03&symbol=QQQ').status_code == 200
    assert mock_alpaca.get_bars_call_count > 0
