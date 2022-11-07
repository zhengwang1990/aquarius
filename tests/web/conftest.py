import os
import subprocess
import time

import alpaca_trade_api as tradeapi
import pytest
import sqlalchemy
from alpharius.web import create_app
from .. import fakes


@pytest.fixture(autouse=True)
def mock_alpaca(mocker):
    client = fakes.FakeAlpaca()
    mocker.patch.object(tradeapi, 'REST', return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_cash_reserve():
    os.environ['CASH_RESERVE'] = '0'


@pytest.fixture(autouse=True)
def mock_subprocess(mocker):
    return mocker.patch.object(subprocess, 'run', side_effect=lambda _: time.sleep(0.1))


@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_engine(mocker):
    os.environ['SQL_STRING'] = 'fake_path'
    engine = fakes.FakeDbEngine()
    mocker.patch.object(sqlalchemy, 'create_engine', return_value=engine)
    return engine
