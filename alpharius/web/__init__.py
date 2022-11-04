import logging
import os
import subprocess

from flask import Flask
from flask_apscheduler import APScheduler
from . import web


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.config.from_mapping(SECRET_KEY=secret_key)

    if test_config:
        app.config.from_mapping(test_config)

    app.logger.setLevel(logging.INFO)
    app.register_blueprint(web.bp)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.task('cron', id='trade', day_of_week='mon-fri',
                    hour=21, minute=0, timezone='America/New_York')
    def trade():
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        bin_file = os.path.join(base_dir, 'bin', 'cron.sh')
        app.logger.info('Start running [%s]', bin_file)
        subprocess.run(['/bin/bash', bin_file])

    return app
