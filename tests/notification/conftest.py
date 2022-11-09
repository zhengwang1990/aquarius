import email.mime.image as image
import email.mime.multipart as multipart
import os
import smtplib

import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pytest
from .. import fakes


@pytest.fixture(autouse=True)
def mock_alpaca(mocker):
    client = fakes.FakeAlpaca()
    mocker.patch.object(tradeapi, 'REST', return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_matplotlib(mocker):
    mocker.patch.object(plt, 'savefig')
    mocker.patch.object(plt, 'tight_layout')
    mocker.patch.object(fm.FontManager, 'addfont')
    mocker.patch.object(fm.FontManager, 'findfont')


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
