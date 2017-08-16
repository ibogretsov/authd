import json
import uuid
import datetime
import bcrypt

import flask
import voluptuous as schema

from authd import dataaccess
from authd import models

root = flask.Blueprint("root", __name__, url_prefix="")
USER_SCHEMA = schema.Schema({
    schema.Required("email"): schema.Email(),
    schema.Required("password"): schema.All(str, schema.Length(min=6))
})


@root.route("/users", methods=["POST"])
def create_user():
    data = json.loads(flask.request.data)
    try:
        USER_SCHEMA(data)
    except flask.MultipleInvalid as e:
        flask.abort(
            flask.make_response(flask.jsonify(message=str(e)), 400)
        )
    password = data["password"].encode()
    hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
    with dataaccess.connect_db(flask.current_app.config["DSN"]) as session:
        user = models.User(
            user_id=str(uuid.uuid4()),
            email=data["email"],
            password=hash_password,
            created=datetime.datetime.utcnow())
        session.add(user)
        session.commit()
    return flask.jsonify({"user_id": user.user_id}), 201
