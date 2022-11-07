import os
import subprocess
import threading

import flask
from flask_apscheduler import APScheduler

app = flask.Flask(__name__)
bp = flask.Blueprint('scheduler', __name__, url_prefix="/scheduler")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
lock = threading.RLock()
job_status = 'idle'


def _trade_impl():
    global job_status, lock
    acquired = lock.acquire(blocking=False)
    if acquired:
        bin_file = os.path.join(BASE_DIR, 'bin', 'trade.sh')
        app.logger.info('Start running [%s]', bin_file)
        job_status = 'running'
        subprocess.run(['/bin/bash', bin_file])
        app.logger.info('Finish running [%s]', bin_file)
        job_status = 'idle'
        lock.release()
    else:
        app.logger.warning('Cannot acquire trade lock')


def get_job_status():
    return job_status


@scheduler.task('cron', id='trade', day_of_week='mon-fri',
                hour='9-15', minute='*', timezone='America/New_York')
def trade():
    if job_status != 'running':
        _trade_impl()


@scheduler.task('cron', id='backfill', day_of_week='mon-fri',
                hour='16,17,21', minute=5, timezone='America/New_York')
def backfill():
    bin_file = os.path.join(BASE_DIR, 'bin', 'backfill.sh')
    app.logger.info('Start running [%s]', bin_file)
    subprocess.run(['/bin/bash', bin_file])
    app.logger.info('Finish running [%s]', bin_file)


@bp.route('/trigger', methods=['POST'])
def trigger():
    app.logger.info('Trade triggered manually')
    t = threading.Thread(target=_trade_impl)
    t.start()
    return ''
