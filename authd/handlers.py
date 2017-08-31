import json
import datetime
import bcrypt

import flask
import voluptuous as schema

from authd import dataaccess
from authd import models

root = flask.Blueprint("root", __name__, url_prefix="")

USER_SCHEMA = schema.Schema({
    schema.Required("email"):
    schema.Email(),
    schema.Required("password"):
    schema.All(str, schema.Length(min=6))
})


@root.route("/users", methods=["POST"])
def create_user():
    data = json.loads(flask.request.data)
    try:
        USER_SCHEMA(data)
    except schema.MultipleInvalid as e:
        flask.abort(flask.make_response(flask.jsonify(message=str(e)), 400))
    password = data["password"].encode()
    hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
    with dataaccess.connect_db(flask.current_app.config["DSN"]) as session:
        # TODO: check if user exits
        existing = session.query(models.User.email).filter(
            models.User.email == data["email"]).first()
        if existing is not None:
            flask.abort(
                flask.make_response(
                    flask.jsonify(message="This user already exists"), 400))
        user = models.User(
            email=data["email"],
            password=hash_password,
            created=datetime.datetime.utcnow())
        session.add(user)
        now = datetime.datetime.utcnow()
        conf = models.Confirm(
            user=user,
            created=now,
            expires=now + datetime.timedelta(seconds=20))
        session.add(conf)
        session.commit()
    return flask.jsonify({
        "user": {
            "id": user.user_id
        },
        "confirmation": {
            "id": conf.conf_id,
            "created": conf.created,
            "expires": conf.expires
        }
    }), 201


@root.route("/actions/<uuid:conf_id>", methods=["GET"])
def confirm_user(conf_id):
    # read confirmation-id from request
    # find confirmation id database by id
    # if confirmation not exists return 404
    # if confirmation expired return 400
    # find user from confirmation
    # set user.active = True
    # delete confirmation
    # return HTTP 200
    with dataaccess.connect_db(flask.current_app.config["DSN"]) as session:
        existing = session.query(models.Confirm).filter(
            models.Confirm.conf_id == str(conf_id)).first()
        if existing is None:
            flask.abort(
                flask.make_response(
                    flask.jsonify(message="confirmation not exists"), 404))
        if existing.expires < datetime.datetime.utcnow():
            flask.abort(
                flask.make_response(
                    flask.jsonify(message="confirmation expired"), 400))
        user_id = existing.user_id
        session.query(models.User).filter(
            models.User.user_id == str(user_id)).update(
                {
                    models.User.active: True
                }, synchronize_session=False)
        session.query(models.Confirm).filter(
            models.Confirm.conf_id == str(conf_id)).delete()
        session.commit()
    return flask.jsonify({
        "user": {
            "id": user_id,
            "active": True
        }
    }), 200
