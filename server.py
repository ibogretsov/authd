import json

import flask

from authd import handlers


def create_app(config_filename):
    app = flask.Flask(__name__)
    with open(config_filename, mode="r", encoding="utf-8") as cfg:
        app.config.update(json.load(cfg))
    app.register_blueprint(handlers.root)
    return app


if __name__ == "__main__":
    app = create_app("authd/authdb.json")
    app.run()
