import time
import threading

import pytest
from alpharius.web import scheduler


def test_trigger(client, mocker):
    thread = mocker.patch.object(threading, 'Thread')

    assert client.post('/scheduler/trigger').status_code == 200
    thread.assert_called_once()


@pytest.mark.parametrize('job_name',
                         ['trade', 'backfill'])
def test_scheduler(job_name):
    job = scheduler.scheduler.get_job(job_name)
    assert job.next_run_time.timestamp() < time.time() + 86400 * 3
