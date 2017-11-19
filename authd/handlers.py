import json
import logging

import flask
import tokenlib

from authd import controller, managers

root = flask.Blueprint("root", __name__, url_prefix="")
LOG = logging.getLogger(__name__)


def abort(message, status_code):
    flask.abort(
        flask.make_response(flask.jsonify(message=message), status_code))


@root.errorhandler(500)
def internal_server_error(exc):
    LOG.error(exc, exc_info=True)
    return flask.render_template("500.html"), 500


@root.route("/users", methods=["POST"])
def create_user():
    data = json.loads(flask.request.data)
    try:
        managers.email_password_correct(data)
    except managers.Incorrect as exc:
        abort(str(exc), 400)
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
        abort(str(exc), 400)
    return flask.jsonify({"user": {"id": user_id, "active": True}}), 200


@root.route("/token", methods=["POST"])
def login():
    data = json.loads(flask.request.data)
    try:
        managers.email_password_correct(data)
    except managers.Incorrect as exc:
        abort(str(exc), 400)
    control = controller.Controller(flask.current_app.config)
    try:
        user_id = control.login(data["email"], data["password"])
    except managers.NotFound as exc:
        abort(str(exc), 401)
    except managers.NotActive as exc:
        abort(str(exc), 400)
    except managers.SecurityError as exc:
        abort(str(exc), 401)
    token = tokenlib.make_token(
        {
            "user_id": user_id
        },
        secret=flask.current_app.config["security"]["key"])
    return flask.jsonify({"token": token}), 200


@root.route("/actions/request_pass_res", methods=["POST"])
def request_password_reset():
    data = json.loads(flask.request.data)
    try:
        managers.email_correct(data)
    except managers.Incorrect as exc:
        abort(str(exc), 400)
    control = controller.Controller(flask.current_app.config)
    try:
        confirmation = control.request_password_reset(data["email"])
    except managers.NotFound as exc:
        abort(str(exc), 404)
    return flask.jsonify({
        "user": {
            "id": confirmation.user_id
        },
        "confirmation": {
            "id": confirmation.confirm_id,
            "created": confirmation.created,
            "expires": confirmation.expires
        }
    }), 201


@root.route("/actions/reset_password/<uuid:confirm_id>", methods=["POST"])
def reset_password(confirm_id):
    data = json.loads(flask.request.data)
    try:
        managers.password_correct(data)
    except managers.Incorrect as exc:
        abort(str(exc), 400)
    control = controller.Controller(flask.current_app.config)
    try:
        control.reset_password(confirm_id, data["password"].encode("utf-8"))
    except managers.NotFound as exc:
        abort(str(exc), 404)
    except managers.Expired as exc:
        abort(str(exc), 400)
    return flask.jsonify({"message": "password changed successfully"}), 200


@root.route("/token", methods=["GET"])
def return_token():
    token = flask.request.headers.get("Authorization")
    try:
        user_id = tokenlib.parse_token(
            token,
            secret=flask.current_app.config["security"]["key"])["user_id"]
    except tokenlib.errors.ExpiredTokenError as exc:
        abort("Token expired", 400)
    except tokenlib.errors.InvalidSignatureError as exc:
        abort("Invalid token", 401)
    except tokenlib.errors.MalformedTokenError as exc:
        abort("Invalid token", 401)
    return flask.jsonify({"user_id": user_id}), 200
