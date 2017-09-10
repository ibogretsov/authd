import json

import bcrypt
import flask
import tokenlib
import voluptuous as schema

from authd import controller, managers

root = flask.Blueprint("root", __name__, url_prefix="")

USER_SCHEMA = schema.Schema({
    schema.Required("email"):
    schema.Email(),
    schema.Required("password"):
    schema.All(str, schema.Length(min=6))
})


def abort(message, status_code, item=None):
    if item is None:
        flask.abort(
            flask.make_response(flask.jsonify(message=message), status_code))
    flask.abort(
        flask.make_response(
            flask.jsonify(message=message, item=item), status_code))


def email_password_correct(data):
    try:
        USER_SCHEMA(data)
    except schema.MultipleInvalid as e:
        abort(str(e), 400)


def return_token(token):
    manager = tokenlib.TokenManager(secret="tokentoken")
    return flask.jsonify(manager.parse_token(token))


@root.route("/users", methods=["POST"])
def create_user():
    data = json.loads(flask.request.data)
    email_password_correct(data)
    password = data["password"].encode("utf-8")
    hash_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
    control = controller.Controller(flask.current_app.config)
    try:
        user, confirmation = control.create_user(data["email"], hash_password)
    except managers.SecurityError as exc:
        abort(str(exc), 400)
    token = tokenlib.make_token(
        {
            "user": {
                "id": user.user_id
            },
            "confirmation": {
                "id": confirmation.conf_id,
                "created": confirmation.created.isoformat(" "),
                "expires": confirmation.expires.isoformat(" ")
            }
        },
        secret=flask.current_app.config["security"]["key"])
    return return_token(token), 201


@root.route("/actions/<uuid:conf_id>", methods=["GET"])
def confirm_user(conf_id):
    control = controller.Controller(flask.current_app.config)
    try:
        user_id = control.confirm_user(conf_id)
    except managers.NotFound as exc:
        abort(str(exc), 404)
    except managers.Expired as exc:
        abort(str(exc), 404, exc.conf_id)
    token = tokenlib.make_token(
        {
            "user": {
                "id": user_id,
                "active": True
            }
        },
        secret=flask.current_app.config["security"]["key"])
    return return_token(token), 200


@root.route("/v1/tokens", methods=["POST"])
def login():
    data = json.loads(flask.request.data)
    email_password_correct(data)
    control = controller.Controller(flask.current_app.config)
    try:
        control.login(data["email"], data["password"])
    except managers.NotFound as exc:
        abort(str(exc), 401)
    except managers.NotActive as exc:
        abort(str(exc), 400)
    except managers.SecurityError as exc:
        abort(str(exc), 401)
    token = tokenlib.make_token(
        {
            "email": data["email"],
            "password": data["password"]
        },
        secret=flask.current_app.config["security"]["key"])
    return return_token(token), 200
