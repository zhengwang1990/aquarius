import os

import pytest
import sqlalchemy

from alpharius.web import create_app
from .. import fakes


@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_cash_reserve(mocker):
    mocker.patch.dict(os.environ, {'CASH_RESERVE': '0'})


@pytest.fixture(autouse=True)
def mock_engine(mocker):
    mocker.patch.dict(os.environ, {'SQL_STRING': 'fake_path'})
    engine = fakes.FakeDbEngine()
    mocker.patch.object(sqlalchemy, 'create_engine', return_value=engine)
    return engine


@pytest.fixture(autouse=True)
def mock_data_client(mocker):
    client = fakes.FakeDataClient()
    mocker.patch('alpharius.data.FmpClient', return_value=client)
    return client
