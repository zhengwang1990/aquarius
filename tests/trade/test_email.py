from alpharius.trade import email


def test_send_alert(mock_smtp):
    client = email.Email()
    client.send_alert('log_file_path', 0, 'email_title')

    mock_smtp.assert_called_once()
