from concurrent import futures

import flask
from .alpaca_client import AlpacaClient

bp = flask.Blueprint('dashboard', __name__)

_client = AlpacaClient()


@bp.route("/")
def dashboard():
    tasks = dict()
    with futures.ThreadPoolExecutor(max_workers=3) as pool:
        tasks['histories'] = pool.submit(_client.get_portfolio_histories)
        tasks['orders'] = pool.submit(_client.get_recent_orders)
        tasks['positions'] = pool.submit(_client.get_current_positions)
        tasks['watch'] = pool.submit(_client.get_market_watch)
    return flask.render_template('dashboard.html',
                                 histories=tasks['histories'].result(),
                                 orders=tasks['orders'].result(),
                                 positions=tasks['positions'].result(),
                                 watch=tasks['watch'].result())
