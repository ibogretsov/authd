import json
import datetime

import bcrypt
import flask
import tokenlib
import voluptuous as schema

from authd import dataaccess, managers

root = flask.Blueprint("root", __name__, url_prefix="")

USER_SCHEMA = schema.Schema({
    schema.Required("email"):
    schema.Email(),
    schema.Required("password"):
    schema.All(str, schema.Length(min=6))
})


def abort(message, status_code):
    flask.abort(
        flask.make_response(flask.jsonify(message=message), status_code))


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
    with dataaccess.connect_db(
            flask.current_app.config["database"]["DSN"]) as session:
        existing = session.query(models.User.email).filter(
            models.User.email == data["email"]).first()
        if existing is not None:
            abort("This user already exists", 400)
        now = datetime.datetime.utcnow()
        expires = now + flask.current_app.config["security"]["ttl"]
        user = models.User(
            email=data["email"], password=hash_password, created=now)
        session.add(user)
        conf = models.Confirm(user=user, created=now, expires=expires)
        session.add(conf)
        session.commit()
    token = tokenlib.make_token(
        {
            "user": {
                "id": user.user_id
            },
            "confirmation": {
                "id": conf.conf_id,
                "created": conf.created.isoformat(" "),
                "expires": conf.expires.isoformat(" ")
            }
        },
        secret=flask.current_app.config["security"]["key"])
    return return_token(token), 201


@root.route("/actions/<uuid:conf_id>", methods=["GET"])
def confirm_user(conf_id):
    with dataaccess.connect_db(
            flask.current_app.config["database"]["DSN"]) as session:
        existing = session.query(models.Confirm).filter(
            models.Confirm.conf_id == str(conf_id)).first()
        if existing is None:
            abort("confirmation not exists", 404)
        if existing.expires < datetime.datetime.utcnow():
            session.query(models.Confirm).filter(
                models.Confirm.conf_id == str(conf_id)).delete()
            now = datetime.datetime.utcnow()
            expires = now + flask.current_app.config["security"]["ttl"]
            conf = models.Confirm(
                user_id=existing.user_id, created=now, expires=expires)
            session.add(conf)
            session.commit()
            flask.abort(
                flask.make_response(
                    flask.jsonify(
                        message="confirmation expired",
                        new_conf_id=conf.conf_id), 404))
        user_id = existing.user_id
        session.query(models.User).filter(
            models.User.user_id == user_id).update(
                {
                    models.User.active: True
                }, synchronize_session=False)
        session.query(models.Confirm).filter(
            models.Confirm.conf_id == str(conf_id)).delete()
        session.commit()
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
    with dataaccess.connect_db(
            flask.current_app.config["database"]["DSN"]) as session:
        user = session.query(models.User.email, models.User.password,
                             models.User.active).filter(
                                 models.User.email == data["email"]).first()
        if user is None:
            abort("this user not found", 401)
        if not user.active:
            abort("his user not active", 400)
        hash_password = user.password.encode("utf-8")
        password = data["password"].encode("utf-8")
        if not bcrypt.checkpw(password, hash_password):
            abort("password doesn't matched", 401)
    token = tokenlib.make_token(
        {
            "email": user.email,
            "password": user.password
        },
        secret=flask.current_app.config["security"]["key"])
    return return_token(token), 200
