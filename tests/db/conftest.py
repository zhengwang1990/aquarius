import os

import alpaca_trade_api as tradeapi
import alpharius.db as db
import sqlalchemy
import pytest
from .. import fakes


@pytest.fixture(autouse=True)
def mock_alpaca(mocker):
    client = fakes.FakeAlpaca()
    mocker.patch.object(tradeapi, 'REST', return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_engine(mocker):
    os.environ['SQL_STRING'] = 'fake_path'
    engine = fakes.FakeDbEngine()
    mocker.patch.object(sqlalchemy, 'create_engine', return_value=engine)
    return engine


@pytest.fixture
def client():
    return db.Db()
