import os

from flask import Flask
from . import db
from .routes import lobby, game, dice, user
import logging


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(lobby.router)
    app.register_blueprint(game.router)
    app.register_blueprint(dice.router)
    app.register_blueprint(user.router)
    log = logging.getLogger('werkzeug')
    # log.setLevel(logging.WARNING)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    return app
