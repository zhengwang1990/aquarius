import time
import threading
from concurrent import futures

import pytest
from alpharius.web import scheduler


def test_trigger(client, mocker):
    thread = mocker.patch.object(threading, 'Thread')

    assert client.post('/trigger').status_code == 200
    thread.assert_called_once()


def test_trade_impl(mocker):
    mock_submit = mocker.Mock()
    mock_pool = mocker.patch.object(futures, 'ProcessPoolExecutor')
    mock_pool.return_value.__enter__.return_value.submit = mock_submit

    scheduler._trade_impl()

    mock_submit.assert_called_once()


def test_backfill(mock_engine):
    scheduler.backfill()

    assert mock_engine.conn.execute.call_count > 0


@pytest.mark.parametrize('job_name',
                         ['trade', 'backfill'])
def test_scheduler(job_name):
    job = scheduler.scheduler.get_job(job_name)
    assert job.next_run_time.timestamp() < time.time() + 86400 * 3
