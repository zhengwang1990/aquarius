import logging
import os

from flask import Flask, render_template
from . import scheduler
from . import web


def handle_exception(e):
    return render_template('exception.html',
                           error_message=str(e))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.config.from_mapping(SECRET_KEY=secret_key)

    if test_config:
        app.config.from_mapping(test_config)

    app.logger.setLevel(logging.INFO)
    app.register_blueprint(web.bp)
    app.register_blueprint(scheduler.bp)
    if secret_key != 'dev':
        app.register_error_handler(Exception, handle_exception)

    return app
