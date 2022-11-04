import textwrap

from alpharius.web import web


def test_dashboard(client, mock_alpaca):
    assert client.get('/').status_code == 200
    assert mock_alpaca.get_portfolio_history_call_count > 0
    assert mock_alpaca.list_orders_call_count > 0
    assert mock_alpaca.list_positions_call_count > 0


def test_transactions(client, mock_alpaca):
    assert client.get('/transactions').status_code == 200
    assert mock_alpaca.list_orders_call_count > 0


def test_logs_no_file(client):
    assert client.get('/logs').status_code == 200


def test_logs_read_file(client, mocker):
    fake_data = textwrap.dedent("""
    [DEBUG] [2022-11-03 10:33:00] [main.py:11] This is debug log.
    [INFO] [2022-11-03 10:34:00] [main.py:12] This is info log.
    [WARNING] [2022-11-03 10:35:00] [main.py:13] This is warning log.
    [ERROR] [2022-11-03 10:36:00] [main.py:14] This is error log.
    More error messages.
    """)
    mocker.patch.object(web, '_read_log_file', return_value=fake_data)

    assert client.get('/logs').status_code == 200
