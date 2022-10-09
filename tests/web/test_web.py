def test_dashboard(client, mock_alpaca):
    assert client.get('/').status_code == 200
    assert mock_alpaca.get_portfolio_history_call_count > 0
    assert mock_alpaca.list_orders_call_count > 0
    assert mock_alpaca.list_positions_call_count > 0


def test_transactions(client, mock_alpaca):
    assert client.get('/transactions').status_code == 200
    assert mock_alpaca.list_orders_call_count > 0
