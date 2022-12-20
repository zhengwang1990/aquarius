import argparse

import pytest
from alpharius.notification import email_sender


def test_send_summary(mock_smtp):
    client = email_sender.EmailSender()
    client.send_summary()

    mock_smtp.assert_called_once()


def test_send_alert(mock_smtp):
    client = email_sender.EmailSender()
    client.send_alert('error_message')

    mock_smtp.assert_called_once()


@pytest.mark.parametrize('mode',
                         ['summary', 'alert'])
def test_main(mode, mocker, mock_smtp):
    mocker.patch.object(
        argparse.ArgumentParser, 'parse_args',
        return_value=argparse.Namespace(mode=mode, error_message='fake message'))

    email_sender.main()

    mock_smtp.assert_called_once()
