import logging
import os

from flask import Flask
from . import web


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.config.from_mapping(SECRET_KEY=secret_key)

    if test_config:
        app.config.from_mapping(test_config)

    app.logger.setLevel(logging.INFO)
    app.register_blueprint(web.bp)

    return app
