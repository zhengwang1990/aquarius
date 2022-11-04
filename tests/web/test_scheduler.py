import time

from alpharius.web import scheduler


def test_trigger(client, mock_subprocess):
    """Trigger twice but only one should run."""
    assert client.post('/scheduler/trigger').status_code == 200
    assert client.post('/scheduler/trigger').status_code == 200
    time.sleep(1)
    mock_subprocess.assert_called_once()


def test_scheduler():
    job = scheduler.scheduler.get_job('trade')
    assert job.next_run_time.timestamp() < time.time() + 86400 * 3
