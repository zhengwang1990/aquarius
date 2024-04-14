import alpaca.trading as alpaca_trading
import alpaca_trade_api as tradeapi
import pytest

from . import fakes


@pytest.fixture(autouse=True)
def mock_alpaca(mocker):
    client = fakes.FakeAlpaca()
    mocker.patch.object(tradeapi, 'REST', return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_trading_client(mocker):
    client = fakes.FakeTradingClient()
    mocker.patch.object(alpaca_trading, 'TradingClient', return_value=client)
    return client
