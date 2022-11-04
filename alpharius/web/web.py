import json
import os
from concurrent import futures

import flask
import pandas as pd

from .alpaca_client import AlpacaClient

bp = flask.Blueprint('web', __name__)


@bp.route('/')
def dashboard():
    client = AlpacaClient()
    tasks = dict()
    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks['histories'] = pool.submit(client.get_portfolio_histories)
        tasks['orders'] = pool.submit(client.get_recent_orders)
        tasks['positions'] = pool.submit(client.get_current_positions)
        tasks['watch'] = pool.submit(client.get_market_watch)
    return flask.render_template('dashboard.html',
                                 histories=json.dumps(tasks['histories'].result()),
                                 orders=tasks['orders'].result(),
                                 positions=tasks['positions'].result(),
                                 watch=tasks['watch'].result())


@bp.route('/transactions')
def transactions():
    client = AlpacaClient()
    return flask.render_template('transactions.html',
                                 transactions=client.get_transactions())


def _read_log_file(log_file: str) -> str:
    log_content = ''
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_content = f.read()
    return log_content


@bp.route('/logs')
def logs():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    log_file = os.path.join(base_dir, 'log.txt')
    log_content = _read_log_file(log_file)
    log_lines = log_content.split('\n')
    log_entries = []
    i = 0
    while i < len(log_lines):
        line = log_lines[i]
        if line.startswith('[') and ']' in line:
            span_start, span_end = 0, 0
            spans = []
            for _ in range(3):
                span_start = line.find('[', span_end)
                span_end = line.find(']', span_start)
                spans.append(line[span_start + 1:span_end])
            message = line[span_end + 1:]
            log_entry = {'type': spans[0].lower(),
                         'time': pd.to_datetime(spans[1]).strftime('%H:%M:%S'),
                         'time-short': pd.to_datetime(spans[1]).strftime('%H:%M'),
                         'code': spans[2],
                         'message': message}
            i += 1
            while i < len(log_lines) and not (log_lines[i].startswith('[') and ']' in log_lines[i]):
                log_entry['message'] += '\n' + log_lines[i]
                i += 1
            if len(log_entry['message']) > 200:
                log_entry['message-short'] = log_entry['message'][:197] + '...'
            log_entries.append(log_entry)
        else:
            i += 1
    return flask.render_template('logs.html',
                                 log_entries=log_entries)
