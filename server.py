import logging.config


import flask

from authd import handlers
from authd import config


def create_app(config_filename):
    app = flask.Flask(__name__)
    app.config.update(config.load(config_filename))
    app.register_blueprint(handlers.root)
    return app


if __name__ == "__main__":
    app = create_app("etc/authdb.json")
    logging.config.dictConfig(app.config["logger"])
    app.run()
