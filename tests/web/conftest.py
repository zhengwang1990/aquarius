import os
from concurrent import futures

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


@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_engine(mocker):
    mocker.patch.dict(os.environ, {'SQL_STRING': 'fake_path'})
    engine = fakes.FakeDbEngine()
    mocker.patch.object(sqlalchemy, 'create_engine', return_value=engine)
    return engine


@pytest.fixture(autouse=True)
def mock_process_pool(mocker):
    mocker.patch.object(futures, 'ProcessPoolExecutor', return_value=fakes.FakeProcessPool())
