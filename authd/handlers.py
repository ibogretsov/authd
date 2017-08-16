import json
import uuid
import time

import flask
import sqlalchemy as sa
from flask import request, make_response, abort, jsonify
from voluptuous import Schema, Email, MultipleInvalid, All, Length

from authd import dataaccess
from authd import models

root = flask.Blueprint("root", __name__, url_prefix="")
schema = Schema({"email": Email(), "password": All(str, Length(min=6))})


@root.route("/users", methods=["POST"])
def create_user():
    data = json.loads(request.data)
    try:
        schema(data)
    except MultipleInvalid as e:
        abort(make_response(jsonify(message=str(e)), 400))
    with dataaccess.connect_db(flask.current_app.config["DSN"]) as session:
        user = models.User(
            user_id=str(uuid.uuid4()),
            **data)
        session.add(user)
        session.commit()
    return jsonify({"user_id": user.user_id}), 201
# {"user": {"id": user.id}}