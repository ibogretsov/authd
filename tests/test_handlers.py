import json

import flask
import pytest
# from authd import dataaccess, models


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


# def test_create_user_exists(client):
#     resp = client.post(
#         "/users",
#         data=json.dumps({
#             "email": "test@mail.com",
#             "password": "123456"
#         }))
#     with dataaccess.connect_db(flask.current_app.config["DSN"]) as sess:
#         existing = sess.query(models.User.email).filter(
#             models.User.email == resp.email).first()
#         if existing is not None:
#             assert resp.status_code == 400
