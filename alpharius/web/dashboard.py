import json

import flask
from .alpaca_client import AlpacaClient

bp = flask.Blueprint('dashboard', __name__)

_client = AlpacaClient()


@bp.route("/")
def dashboard():
    histories = _client.get_portfolio_histories()
    return flask.render_template('dashboard.html', histories=histories)
