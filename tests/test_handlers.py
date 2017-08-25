import json

import flask
# import pytest
from authd import dataaccess, models


def test_create_user_if_email_is_invalid(client):
    resp = client.post(
        "/users", data=json.dumps({
            "email": "invalid",
            "password": "123456"
        }))
    assert resp.status_code == 400


def test_create_user_if_password_is_short(client):
    resp = client.post(
        "/users", data=json.dumps({
            "email": "test@mail.com",
            "password": "1"
        }))
    assert resp.status_code == 400


# def test_user_create_ok(client):
#     data = json.dumps({"email": "test10@mail.com", "password": "123456"})
#     resp = client.post("/users", data=data)
#     data = json.loads(data)
#     with dataaccess.connect_db(flask.current_app.config["DSN"]) as sess:
#         existing = sess.query(models.User).filter(
#             models.User.email == data["email"]).first()
#         if existing is None:
#             assert resp.status_code == 201


def test_create_user(client):
    data = json.dumps({"email": "test11@mail.com", "password": "123456"})
    resp = client.post("/users", data=data)
    data = json.loads(data)
    with dataaccess.connect_db(flask.current_app.config["DSN"]) as sess:
        existing = sess.query(models.Userl).filter(
            models.User.email == data["email"]).first()
        if existing is not None:
            assert resp.status_code == 400
        else:
            # global conf_id
            # conf_id = sess.query(models.Confirm.conf_id).join(
            #     models.User.user_id == models.Confirm.user_id).first()
            assert resp.status_code == 201


# def test_confirmation(client):
#     with dataaccess.connect_db(flask.current_app.config["DSN"]) as sess:
#         existing = sess.query(models.Confirm).filter(
#             models.Confirm.conf_id == conf_id).first()
#         if existing is None:
#             assert resp.status_code == 