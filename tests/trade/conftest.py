import email.mime.image as image
import email.mime.multipart as multipart
import os
import smtplib

import alpaca_trade_api as tradeapi
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import polygon
import pytest
from .. import fakes


@pytest.fixture(autouse=True)
def mock_alpaca(mocker):
    client = fakes.FakeAlpaca()
    mocker.patch.object(tradeapi, 'REST', return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_polygon(mocker):
    mocker.patch.dict(os.environ, {'POLYGON_API_KEY': 'fake_polygon_api_key'})
    client = fakes.FakePolygon()
    mocker.patch.object(polygon, 'RESTClient', return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_pandas(mocker):
    mocker.patch.object(pd.DataFrame, 'to_csv')


@pytest.fixture(autouse=True)
def mock_matplotlib(mocker):
    mocker.patch.object(plt, 'savefig')
    mocker.patch.object(plt, 'tight_layout')
    mocker.patch.object(fm.FontManager, 'addfont')
    mocker.patch.object(fm.FontManager, 'findfont')


@pytest.fixture(autouse=True)
def mock_os(mocker):
    mocker.patch('builtins.open', mocker.mock_open(read_data='data'))
    mocker.patch.object(os.path, 'isfile', return_value=False)
    mocker.patch.object(os, 'makedirs')


@pytest.fixture(autouse=True)
def mock_email(mocker):
    mocker.patch.object(image, 'MIMEImage', autospec=True)
    mocker.patch.object(multipart.MIMEMultipart, 'as_string', return_value='')
    mocker.patch.dict(os.environ, {'EMAIL_USERNAME': 'fake_user',
                                   'EMAIL_PASSWORD': 'fake_password',
                                   'EMAIL_RECEIVER': 'fake_receiver'})


@pytest.fixture(autouse=True)
def mock_smtp(mocker):
    return mocker.patch.object(smtplib, 'SMTP', autospec=True)
