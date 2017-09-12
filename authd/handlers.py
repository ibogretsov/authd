import json

import flask
import tokenlib

from authd import controller, managers

root = flask.Blueprint("root", __name__, url_prefix="")


def abort(message, status_code, item=None):
    if item is None:
        flask.abort(
            flask.make_response(flask.jsonify(message=message), status_code))
    flask.abort(
        flask.make_response(
            flask.jsonify(message=message, item=item), status_code))


@root.route("/users", methods=["POST"])
def create_user():
    data = json.loads(flask.request.data)
    managers.email_password_correct(data, abort)
    control = controller.Controller(flask.current_app.config)
    try:
        user, confirmation = control.create_user(
            data["email"], data["password"].encode("utf-8"))
    except managers.SecurityError as exc:
        abort(str(exc), 400)
    return flask.jsonify({
        "user": {
            "id": user.user_id
        },
        "confirmation": {
            "id": confirmation.confirm_id,
            "created": confirmation.created,
            "expires": confirmation.expires
        }
    }), 201


@root.route("/actions/<uuid:confirm_id>", methods=["GET"])
def confirm_user(confirm_id):
    control = controller.Controller(flask.current_app.config)
    try:
        user_id = control.confirm_user(confirm_id)
    except managers.NotFound as exc:
        abort(str(exc), 404)
    except managers.Expired as exc:
        abort(str(exc), 404, exc.confirm_id)
    return flask.jsonify({"user": {"id": user_id, "active": True}}), 200


@root.route("/v1/tokens", methods=["POST"])
def login():
    data = json.loads(flask.request.data)
    managers.email_password_correct(data, abort)
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
    return token, 200


@root.route("/actions/request_pass_res", methods=["POST"])
def request_password_reset():
    data = json.loads(flask.request.data)
    # managers.email_correct(data["email"], abort)
    control = controller.Controller(flask.current_app.config)
    try:
        confirmation = control.request_password_reset(data["email"])
    except managers.NotFound as exc:
        abort(str(exc), 404)
    return flask.jsonify({
        "confirmation": {
            "id": confirmation.confirm_id,
            "user_id": confirmation.user_id,
            "created": confirmation.created,
            "expires": confirmation.expires
        }
    }), 201


@root.route("/actions/reset_password/<uuid:confirm_id>", methods=["POST"])
def reset_password(confirm_id):
    data = json.loads(flask.request.data)
    managers.password_correct(data["password"], abort)
    control = controller.Controller(flask.current_app.config)
    try:
        control.reset_password(confirm_id, data["password"])
    except managers.NotFound as exc:
        abort(str(exc), 404)
    except managers.Expired as exc:
        abort(str(exc), 404, exc.confirm_id)
    return 200
