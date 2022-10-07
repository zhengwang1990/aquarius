import pandas as pd
from alpharius import trade


def test_get_nasdaq100():
    nasdaq100_symbols = trade.get_nasdaq100(pd.to_datetime('2015-01-01'))
    assert 'AAPL' in nasdaq100_symbols


def test_get_sp500():
    sp500_symbols = trade.get_sp500(pd.to_datetime('1999-01-01'))
    assert 'AAPL' in sp500_symbols
