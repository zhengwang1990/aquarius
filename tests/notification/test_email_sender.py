from alpharius.notification import email_sender


def test_send_summary(mock_smtp):
    client = email_sender.EmailSender()
    client.send_summary()

    mock_smtp.assert_called_once()


def test_send_alert(mock_smtp):
    client = email_sender.EmailSender()
    client.send_alert('error_message')

    mock_smtp.assert_called_once()
