import os
import threading
import traceback

import flask
from alpharius.db import Db
from alpharius.trade import trading
from alpharius.notification.email_sender import EmailSender
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
        app.logger.info('Start trading')
        job_status = 'running'
        try:
            trading()
        except Exception as e:
            error_message = str(e) + '\n' + ''.join(traceback.format_tb(e.__traceback__))
            app.logger.error('Fail in trading: %s', error_message)
            EmailSender().send_alert(error_message)
        app.logger.info('Finish trading')
        job_status = 'idle'
        lock.release()
    else:
        app.logger.warning('Cannot acquire trade lock')


def get_job_status():
    return job_status


@scheduler.task('cron', id='trade', day_of_week='mon-fri',
                hour='*', minute='*/30', timezone='America/New_York')
def trade():
    if job_status != 'running':
        t = threading.Thread(target=_trade_impl)
        t.start()


@scheduler.task('cron', id='backfill', day_of_week='mon-fri',
                hour='16,17,22', minute=15, timezone='America/New_York')
def backfill():
    app.logger.info('Start backfilling')
    try:
        Db().backfill()
    except Exception as e:
        error_message = str(e) + '\n' + ''.join(traceback.format_tb(e.__traceback__))
        app.logger.error('Fail in trading: %s', error_message)
        EmailSender().send_alert(error_message)
    app.logger.info('Finish backfilling')


@bp.route('/trigger', methods=['POST'])
def trigger():
    app.logger.info('Trade triggered manually')
    t = threading.Thread(target=_trade_impl)
    t.start()
    return ''
