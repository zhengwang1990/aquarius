import collections
import datetime
import math
import json
from concurrent import futures
from typing import List

import flask
import numpy as np
import pandas as pd
from alpharius.db import Aggregation, Db
from alpharius.utils import (
    compute_drawdown, compute_risks, get_signed_percentage,
    get_colored_value, TIME_ZONE,
)
from .alpaca_client import AlpacaClient
from .scheduler import get_job_status

bp = flask.Blueprint('web', __name__)


def _get_dashdata():
    client = AlpacaClient()
    tasks = dict()
    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks['histories'] = pool.submit(client.get_portfolio_histories)
        tasks['orders'] = pool.submit(client.get_recent_orders)
        tasks['positions'] = pool.submit(client.get_current_positions)
        tasks['watch'] = pool.submit(client.get_market_watch)
    return {'histories': tasks['histories'].result(),
            'orders': tasks['orders'].result(),
            'positions': tasks['positions'].result(),
            'watch': tasks['watch'].result()}


@bp.route('/')
def dashboard():
    data = _get_dashdata()
    return flask.render_template('dashboard.html',
                                 histories=json.dumps(data['histories']),
                                 orders=data['orders'],
                                 positions=data['positions'],
                                 watch=data['watch'])


@bp.route('/dashdata')
def dashdata():
    data = _get_dashdata()
    return json.dumps(data)


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
            'link': (f'experiments?symbol={t.symbol}&'
                     f'date={pd.to_datetime(t.exit_time).tz_convert(TIME_ZONE).strftime("%F")}')
        })
    return flask.render_template('transactions.html',
                                 transactions=trans,
                                 current_page=page,
                                 total_page=total_page)


def _shift_to_last(arr, target_value):
    for i in range(len(arr)):
        if arr[i] == target_value:
            for j in range(i + 1, len(arr)):
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
            break


def _get_stats(aggs: List[Aggregation]):
    stats = dict()
    transaction_cnt = []
    for agg in aggs:
        processor = agg.processor
        if processor not in stats:
            stats[processor] = {'gl': 0, 'gl_pct_acc': 0, 'cnt': 0, 'win_cnt': 0,
                                'slip': 0, 'slip_pct_acc': 0, 'slip_cnt': 0}
        stats[processor]['gl'] += agg.gl
        stats[processor]['cnt'] += agg.count
        stats[processor]['win_cnt'] += agg.win_count
        stats[processor]['slip'] += agg.slippage
        if agg.slippage_count > 0:
            stats[processor]['slip_pct_acc'] += agg.avg_slippage_pct * agg.slippage_count
            stats[processor]['slip_cnt'] += agg.slippage_count
    total_stats = dict()
    for processor, stat in stats.items():
        transaction_cnt.append({'processor': processor, 'cnt': stat['cnt']})
        for k, v in stat.items():
            if processor == 'UNKNOWN' and k in ['slip', 'slip_pct_acc', 'slip_cnt']:
                continue
            if k not in total_stats:
                total_stats[k] = 0
            total_stats[k] += v
    stats['ALL'] = total_stats
    transaction_cnt.sort(key=lambda entry: entry['cnt'], reverse=True)

    for processor, stat in stats.items():
        stat['processor'] = processor
        stat['avg_slip_pct'] = (get_signed_percentage(stat['slip_pct_acc'] / stat['slip_cnt'])
                                if stat.get('slip_cnt', 0) > 0 and processor != 'UNKNOWN' else 'N/A')
        win_rate = stat['win_cnt'] / stat['cnt'] if stat.get('cnt', 0) > 0 else 0
        stat['win_rate'] = f'{win_rate * 100:.2f}%'
        for k in ['gl', 'slip']:
            v = stat.get(k, 0)
            color = 'green' if v >= 0 else 'red'
            if k == 'slip' and processor == 'UNKNOWN':
                stat[k] = 'N/A'
            else:
                stat[k] = get_colored_value(f'{v:,.2f}', color)

    # Order stats alphabetically with 'UNKNOWN' and 'ALL' appearing at last
    processors = sorted(stats.keys())
    _shift_to_last(processors, 'UNKNOWN')
    _shift_to_last(processors, 'ALL')
    return [stats[processor] for processor in processors], transaction_cnt


def _get_gl_bars(aggs: List[Aggregation]):
    dated_values = {'Daily': collections.defaultdict(int),
                    'Monthly': collections.defaultdict(int)}
    processors = set()
    processors_aggs = collections.defaultdict(list)
    for agg in aggs:
        dated_values['Daily'][agg.date.strftime('%F')] += agg.gl
        dated_values['Monthly'][agg.date.strftime('%Y-%m')] += agg.gl
        processors.add(agg.processor)
        processors_aggs[agg.processor].append(agg)
    num_cuts = {'Daily': 60, 'Monthly': 48}
    labels = dict()
    values = dict()
    all_processors = 'ALL PROCESSORS'
    for timeframe in ['Daily', 'Monthly']:
        labels[timeframe] = sorted(dated_values[timeframe].keys())[-num_cuts[timeframe]:]
        all_gl = [dated_values[timeframe][label] for label in labels[timeframe]]
        values[timeframe] = {all_processors: all_gl}
        for processor in processors:
            processor_values = collections.defaultdict(int)
            for agg in processors_aggs[processor]:
                processor_values[agg.date.strftime('%F')] = agg.gl
                processor_values[agg.date.strftime('%Y-%m')] += agg.gl
            processor_gl = [processor_values.get(label, 0) for label in labels[timeframe]]
            values[timeframe][processor] = processor_gl
    processors = [all_processors] + sorted(processors)
    _shift_to_last(processors, 'UNKNOWN')
    gl_bars = {'labels': labels, 'values': values}
    return gl_bars, processors


def _get_annual_return(daily_price):
    dates = daily_price['dates']
    res = {
        'symbols': daily_price['symbols'],
        'years': [],
        'returns': [[] for _ in daily_price['symbols']],
    }
    if len(dates) < 2:
        return res
    years = []
    values = daily_price['values']
    spots = [[value[0]] for value in values]
    for i in range(len(dates) - 1):
        if dates[i][:4] != dates[i + 1][:4]:
            years.append(dates[i][:4])
            for j in range(len(values)):
                spots[j].append(values[j][i])
    years.append(dates[-1][:4])
    for j in range(len(values)):
        spots[j].append(values[j][-1])
    res['years'] = years
    for j in range(len(spots)):
        res['returns'][j] = [(spots[j][k + 1] / spots[j][k] - 1) * 100
                             for k in range(len(spots[j]) - 1)]
    return res


def _get_risks(daily_prices):
    def get_factors(v, mv):
        a, b, s = compute_risks(v, mv)
        d = compute_drawdown(v)
        r = v[-1] / v[0] - 1
        return {'alpha': get_signed_percentage(a) if a != math.nan else 'N/A',
                'beta': f'{b:.2f}' if b != math.nan else 'N/A',
                'sharpe': f'{s:.2f}' if s != math.nan else 'N/A',
                'drawdown': get_signed_percentage(d),
                'return': get_signed_percentage(r)}

    dates = daily_prices['dates']
    values = daily_prices['values'][daily_prices['symbols'].index('My Portfolio')]
    market_values = daily_prices['values'][daily_prices['symbols'].index('SPY')]
    current_start = 0
    res = []
    for i in range(len(dates)):
        if i != len(dates) - 1 and dates[i][:4] == dates[i + 1][:4]:
            continue
        current_values = values[current_start:i + 1]
        current_market_values = market_values[current_start:i + 1]
        factors = get_factors(current_values, current_market_values)
        factors['year'] = dates[i][:4]
        res.append(factors)
        current_start = i
    overall_factors = get_factors(values, market_values)
    overall_factors['year'] = 'ALL'
    annualized_return = (values[-1] / values[0]) ** (252 / len(values)) - 1
    overall_factors['return'] = get_signed_percentage(annualized_return)
    res.append(overall_factors)
    return res[-6:]  # only show risk factors for last 5 years


@bp.route('/analytics')
def analytics():
    alpaca_client = AlpacaClient()
    with futures.ThreadPoolExecutor(max_workers=1) as pool:
        get_daily_price_task = pool.submit(alpaca_client.get_daily_prices)
    db_client = Db()
    aggs = db_client.list_aggregations()
    stats, transaction_cnt = _get_stats(aggs)
    gl_bars, processors = _get_gl_bars(aggs)
    daily_price = get_daily_price_task.result()
    annual_return = _get_annual_return(daily_price)
    risks = _get_risks(daily_price)
    return flask.render_template('analytics.html',
                                 stats=stats,
                                 transaction_cnt=transaction_cnt,
                                 gl_bars=gl_bars,
                                 annual_return=annual_return,
                                 risks=risks,
                                 processors=processors)


def _parse_log_content(content: str):
    def is_entry_start(lin: str):
        ll = lin.lower()
        return (ll.startswith('[info] [') or ll.startswith('[warning] [')
                or ll.startswith('[debug] [') or ll.startswith('[error] ['))

    log_lines = content.split('\n')
    log_entries = []
    i = 0
    while i < len(log_lines):
        line = log_lines[i]
        if is_entry_start(line):
            span_start, span_end = 0, 0
            spans = []
            for _ in range(3):
                span_start = line.find('[', span_end)
                span_end = line.find(']', span_start)
                spans.append(line[span_start + 1:span_end])
            message = line[span_end + 1:]
            log_type = spans[0].lower()
            log_entry = {'type': log_type,
                         'type_initial': log_type[0],
                         'time': pd.to_datetime(spans[1]).strftime('%H:%M:%S'),
                         'time_short': pd.to_datetime(spans[1]).strftime('%H:%M'),
                         'code': spans[2],
                         'message': message}
            i += 1
            while i < len(log_lines) and not is_entry_start(log_lines[i]):
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
                                 dates=dates)


@bp.route('/experiments')
def experiments():
    client = AlpacaClient()
    date = flask.request.args.get('date')
    start_date = flask.request.args.get('start_date')
    end_date = flask.request.args.get('end_date')
    if start_date and end_date:
        pd_start = pd.to_datetime(start_date)
        if pd_start.isoweekday() > 5:
            pd_start += datetime.timedelta(days=8 - pd_start.isoweekday())
        start_date = pd_start.strftime('%F')
        pd_end = pd.to_datetime(end_date)
        if pd_end.isoweekday() > 5:
            pd_end -= datetime.timedelta(days=pd_end.isoweekday() - 5)
        end_date = pd_end.strftime('%F')
    symbol = flask.request.args.get('symbol')
    all_symbols = client.get_all_symbols()
    return flask.render_template('experiments.html',
                                 all_symbols=all_symbols,
                                 init_date=date,
                                 init_start_date=start_date,
                                 init_end_date=end_date,
                                 init_symbol=symbol)


@bp.route('/charts')
def charts():
    client = AlpacaClient()
    timeframe = flask.request.args.get('timeframe')
    if timeframe == 'intraday':
        start_date = flask.request.args.get('date')
        end_date = start_date
    elif timeframe == 'daily':
        start_date = flask.request.args.get('start_date')
        end_date = flask.request.args.get('end_date')
    else:
        return ''
    symbol = flask.request.args.get('symbol')
    res = client.get_charts(start_date=start_date, end_date=end_date,
                            symbol=symbol, timeframe=timeframe)
    return json.dumps(res)


@bp.route('/job_status')
def job_status():
    return get_job_status()
