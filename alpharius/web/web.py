import itertools
import json
from concurrent import futures

import flask
import numpy as np
import pandas as pd
import pytz
from alpharius.db import Db
from alpharius.utils import get_signed_percentage, get_colored_value
from .alpaca_client import AlpacaClient
from .scheduler import get_job_status

bp = flask.Blueprint('web', __name__)

TIME_ZONE = pytz.timezone('America/New_York')


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
                                 watch=tasks['watch'].result(),
                                 job_status=get_job_status())


@bp.route('/transactions')
def transactions():
    items_per_page = 20
    page = flask.request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    client = Db()
    count = client.get_transaction_count()
    total_page = max(int(np.ceil(count / items_per_page)), 1)
    page = max(min(page, total_page), 1)
    offset = (page - 1) * items_per_page
    trans = []
    time_fmt = f'<span class="med-hidden">%Y-%m-%d </span>%H:%M'
    for t in client.list_transactions(items_per_page, offset):
        trans.append({
            'symbol': t.symbol,
            'side': 'long' if t.is_long else 'short',
            'processor': t.processor if t.processor is not None else '',
            'entry_price': f'{t.entry_price:.4g}',
            'exit_price': f'{t.exit_price:.4g}',
            'entry_time': pd.to_datetime(t.entry_time).tz_convert(TIME_ZONE).strftime(time_fmt),
            'exit_time': pd.to_datetime(t.exit_time).tz_convert(TIME_ZONE).strftime(time_fmt),
            'gl': get_colored_value(f'{t.gl:+,.2f} ({t.gl_pct * 100:+.2f}%)',
                                    'green' if t.gl >= 0 else 'red'),
            'gl_pct': get_signed_percentage(t.gl_pct),
            'slippage': get_colored_value(f'{t.slippage:+,.2f} ({t.slippage_pct * 100:+.2f}%)',
                                          'green' if t.slippage >= 0 else 'red') if t.slippage is not None else '',
            'slippage_pct': get_signed_percentage(t.slippage_pct) if t.slippage_pct is not None else '',
        })
    return flask.render_template('transactions.html',
                                 transactions=trans,
                                 current_page=page,
                                 total_page=total_page,
                                 job_status=get_job_status())


@bp.route('/analytics')
def analytics():
    client = Db()
    aggs = client.list_aggregations()
    proc_stats = dict()
    for agg in aggs:
        processor = agg.processor
        if processor not in proc_stats:
            proc_stats[processor] = {'gl': 0, 'gl_pct_acc': 0, 'cnt': 0, 'win_cnt': 0,
                                     'slip': 0, 'slip_pct_acc': 0, 'slip_cnt': 0}
        proc_stats[processor]['gl'] += agg.gl
        proc_stats[processor]['cnt'] += agg.count
        proc_stats[processor]['win_cnt'] += agg.win_count
        proc_stats[processor]['slip'] += agg.slippage
        if agg.slippage_count > 0:
            proc_stats[processor]['slip_pct_acc'] += agg.avg_slippage_pct * agg.slippage_count
            proc_stats[processor]['slip_cnt'] += agg.slippage_count
    total_stats = dict()
    for stat in proc_stats.values():
        for k, v in stat.items():
            if k not in total_stats:
                total_stats[k] = 0
            total_stats[k] += v

    for stat in itertools.chain(proc_stats.values(), [total_stats]):
        stat['avg_slip_pct'] = (get_signed_percentage(stat['slip_pct_acc'] / stat['slip_cnt'])
                                if stat.get('slip_cnt', 0) > 0 else 'N/A')
        win_rate = stat['win_cnt'] / stat['cnt'] if stat.get('cnt', 0) > 0 else 0
        stat['win_rate'] = f'{win_rate * 100:.2f}%'
        for k in ['gl', 'slip']:
            v = stat.get(k, 0)
            color = 'green' if v >= 0 else 'red'
            stat[k] = get_colored_value(f'{v:,.2f}', color)

    return flask.render_template('analytics.html',
                                 proc_stats=proc_stats,
                                 total_stats=total_stats,
                                 processors=sorted(proc_stats.keys()),
                                 job_status=get_job_status())


def _parse_log_content(content: str):
    log_lines = content.split('\n')
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
                         'time_short': pd.to_datetime(spans[1]).strftime('%H:%M'),
                         'code': spans[2],
                         'message': message}
            i += 1
            while i < len(log_lines) and not (log_lines[i].startswith('[') and ']' in log_lines[i]):
                log_entry['message'] += '\n' + log_lines[i]
                i += 1
            log_entry['message'] = log_entry['message'].lstrip()
            log_entries.append(log_entry)
        else:
            i += 1
    return log_entries


@bp.route('/logs')
def logs():
    client = Db()
    dates = client.list_log_dates()
    date = flask.request.args.get('date')
    if (not date or date not in dates) and dates:
        date = dates[-1]
    results = client.get_logs(date) if date else []
    loggers = []
    log_entries = dict()
    for logger, content in results:
        loggers.append(logger)
        log_entries[logger] = _parse_log_content(content)
    loggers.sort()
    for i in range(len(loggers)):
        if loggers[i] == 'Trading':
            for j in range(i - 1, -1, -1):
                loggers[j + 1] = loggers[j]
            loggers[0] = 'Trading'

    return flask.render_template('logs.html',
                                 loggers=loggers,
                                 log_entries=log_entries,
                                 date=date,
                                 dates=dates,
                                 job_status=get_job_status())
