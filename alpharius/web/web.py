from concurrent import futures

import flask
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
                                 histories=tasks['histories'].result(),
                                 orders=tasks['orders'].result(),
                                 positions=tasks['positions'].result(),
                                 watch=tasks['watch'].result())


@bp.route('/transactions')
def transactions():
    client = AlpacaClient()
    return flask.render_template('transactions.html',
                                 transactions=client.get_transactions())
