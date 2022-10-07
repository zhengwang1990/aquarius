import flask

bp = flask.Blueprint('dashboard', __name__)


@bp.route("/")
def dashboard():
    return flask.render_template('dashboard.html')
